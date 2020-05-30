#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Copyright 2019-2020 Airinnova AB and the FramAT authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------

# Author: Aaron Dettmann

"""
Module for creating the geometric mesh
"""

from collections import OrderedDict
from collections.abc import MutableMapping
from math import ceil

from mframework import FeatureSpec
import numpy as np

from ._element import Element
from ._log import logger
from ._util import Schemas as S
from ._util import pairwise



def create_mesh(m):
    """Top-level function for mesh creation"""

    r = m.results
    abm = AbstractBeamMesh()

    for i, mbeam in enumerate(m.iter('beam')):
        logger.info(f"Meshing beam with index {i}...")

        # Support points (= named nodes)
        sup_points = OrderedDict()
        for node in mbeam.iter('node'):
            sup_points[node['uid']] = node['coord']

        # Element lookup object for the new beam
        elemlu = abm.add_beam_line(sup_points, n=mbeam.get('nelem'))
        logger.info(f"Beam {i} has {elemlu.nelem} elements")

        # ----- Beam element properties -----
        for pdef in mbeam.get('orientation'):
            for elem in elemlu[(pdef['from'], pdef['to'])]:
                elem.set('up', pdef['up'])

        for pdef in mbeam.get('material'):
            for elem in elemlu[(pdef['from'], pdef['to'])]:
                for p in ('E', 'G', 'rho'):
                    val = m.get('material').get(p)  # TODO: non-singleton
                    elem.set(p, val)

        for pdef in mbeam.get('cross_section'):
            for elem in elemlu[(pdef['from'], pdef['to'])]:
                for p in ('A', 'Iy', 'Iz', 'J'):
                    val = m.get('cross_section').get(p)  # TODO: non-singleton
                    elem.set(p, val)

        for pdef in mbeam.get('point_load'):
            (node_id, elem) = elemlu[pdef['at']]
            elem.add('point_load', {'load': pdef['load'], 'node': node_id, 'local_sys': True})

    # # ----- Boundary conditions -----
    # bc = m.get('bc')

    # for pdef in bc.iter('fix'):
    #     abc.set_attr('fix')
    #     elem = elemlu[pdef['at']]
    #     elem.set_attr('point_load', pdef['load'], applies_to=elem.node_id(pdef['at']))

    rmesh = r.set_feature('mesh')
    rmesh.set('abm', abm)


class Point:

    def __init__(self, coord, *, rel_coord=None, uid=None):
        assert uid is None or isinstance(uid, str)
        assert isinstance(coord, (list, np.ndarray)) and len(coord) == 3

        self.coord = np.array(coord)
        self.rel_coord = rel_coord
        self.uid = uid

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.coord!r}, {self.rel_coord!r}, {self.uid!r})"


class LineSegment:

    def __init__(self, p1, p2):
        assert isinstance(p1, Point) and isinstance(p2, Point)

        self.p1 = p1
        self.p2 = p2

        # Set the relative coordinates of the start and end point
        self.p1.rel_coord = 0
        self.p2.rel_coord = 1

        # Line direction
        self.dir = self.p2.coord - self.p1.coord
        self.len = np.linalg.norm(self.dir)
        self.all_points = [p1, p2]

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.p1!r}, {self.p2!r})"

    @property
    def from_uid(self):
        return self.p1.uid

    @property
    def to_uid(self):
        return self.p2.uid

    def split_into(self, n):
        """
        Split segment into smaller segments

        The new line segment will have n + 1 nodes.
        """

        assert isinstance(n, int) and n > 0

        self.all_points = [self.p1, ]

        for i in range(1, n):
            rel_coord = i/n
            self.all_points.append(
                Point(self.p1.coord + rel_coord*self.dir, rel_coord=rel_coord, uid=None)
            )

        self.all_points.append(self.p2)
        return self.all_points

    def iter_points(self, *, exclude_last=False):
        all_points = self.all_points[:-1] if exclude_last else self.all_points
        for p in all_points:
            yield p


class PolygonalChain:

    def __init__(self, sup_points, n=10):
        """
        Polygonal chain

        Args:
            :sup_points: (dict) key: support point uid, value: nodes coordinates
            :n: (int) number of elements for the entire chain

        Attr:
            :segments: (list) line segment
            :len: (float) length of the polygon
        """

        # Ensure that dictionary items are ordered correctly
        assert isinstance(sup_points, OrderedDict)
        assert isinstance(n, int)

        self.node_uids = sup_points.keys()
        self.segments = []
        self.len = 0

        # Add line segments
        points = []
        for uid, coord in sup_points.items():
            points.append(Point(coord, rel_coord=None, uid=uid))

        edges = []
        for p1, p2 in pairwise(points):
            edges.append(LineSegment(p1, p2))

        for seg in edges:
            self.add_segment(seg)

        self.set_node_num(n)

    def __repr__(self):
        return f"< {self.__class__.__qualname__} for {self.node_uids!r} >"

    def add_segment(self, seg):
        assert isinstance(seg, LineSegment)
        self.segments.append(seg)
        self.len += seg.len

    def set_node_num(self, n):
        for seg in self.segments:
            n_seg = ceil(n*(seg.len/self.len))
            seg.split_into(n_seg)

    def iter_points(self):
        curr_len = 0
        # All but last segments...
        for seg in self.segments[:-1]:
            for p in seg.iter_points(exclude_last=True):
                eta_poly = curr_len/self.len + p.rel_coord*(seg.len/self.len)
                yield Point(p.coord, rel_coord=eta_poly, uid=p.uid)
            curr_len += seg.len

        # Last segment...
        seg = self.segments[-1]
        for p in seg.iter_points(exclude_last=False):
            eta_poly = curr_len/self.len + p.rel_coord*(seg.len/self.len)  # TODO: duplicate
            yield Point(p.coord, rel_coord=eta_poly, uid=p.uid)

# ===== Abstract beam element =====

schema_load = {'load': S.vector6x1, 'node': S.pos_int, 'local_sys': {'type': bool}}
schema_mass = {'mass': {'type': S.pos_number}, 'node': S.pos_int}

fspec = FeatureSpec()

for p in Element.PROP_TYPES:
    fspec.add_prop_spec(p, S.pos_number)

fspec.add_prop_spec('up', S.vector3x1)
fspec.add_prop_spec('point_load', schema_load, singleton=False)
fspec.add_prop_spec('dist_load', schema_load, singleton=False)
fspec.add_prop_spec('point_mass', schema_mass, singleton=False)

# =================================


class AbstractEdgeElement(fspec.user_class):

    NUM = 0

    def __init__(self, p1, p2):
        """
        Edge element defined by spatial coordinates and abstract attributes

        Args:
            :p1: (obj) Point object of start point
            :p2: (obj) Point object of end point
        """

        super().__init__()

        self.NUM += 1

        assert isinstance(p1, Point) and isinstance(p2, Point)
        self.p1 = p1
        self.p2 = p2

    def __repr__(self):
        return f"< {self.__class__.__qualname__}({self.p1!r}, {self.p2!r}) >"


class AbstractBeamMesh:

    def __init__(self):
        """
        Mesh consisting of multiple, disconnected polygonal chains. The mesh
        may have globally defined abstract attributes.

        Attr:
            :beams: (list) list of beam look-up objects
        """

        # Each beam has a lookup dict object
        self.beams = []

        self.named_nodes = {}

    def __repr__(self):
        return f"< {self.__class__.__qualname__} for {self.beams!r} >"

    def add_beam_line(self, sup_points, n=10):
        for uid, coord in sup_points.items():
            self.named_nodes[uid] = np.array(coord)

        polygon = PolygonalChain(sup_points, n=n)
        elemlu = ElementLookup()
        for p1, p2 in pairwise(polygon.iter_points()):
            elemlu.elements.append(AbstractEdgeElement(p1, p2))
        self.beams.append(elemlu)
        return self.beams[-1]

    @property
    def nbeams(self):
        return len(self.beams)

    @property
    def nnodes(self):
        return sum([beam.nnodes for beam in self.beams])

    def ndofs(self, ndof_per_node=6):
        return self.nnodes*ndof_per_node

    def get_lims(self):
        x_max = 0
        y_max = 0
        z_max = 0
        x_min = 0
        y_min = 0
        z_min = 0
        for beam in self.beams:
            (x_minb, x_maxb), (y_minb, y_maxb), (z_minb, z_maxb) = beam.get_lims()
            if x_maxb > x_max:
                x_max = x_maxb
            if y_maxb > y_max:
                y_max = y_maxb
            if z_maxb > z_max:
                z_max = z_maxb
            if x_minb < x_min:
                x_min = x_minb
            if y_minb < y_min:
                y_min = y_minb
            if z_minb < z_min:
                z_min = z_minb
        return (x_min, x_max), (y_min, y_max), (z_min, z_max)


class ElementLookup(MutableMapping):

    def __init__(self):
        """
        Group of elements (e.g. comprising a polygonal chain). Individual
        elements or ranges of elements can be looked up with node UIDs.

        Args:
            :elements: (list) list of all elements in this lookup object
        """

        # Dummy
        self._mapping = {}
        self.elements = []

    def __setitem__(self, key, value):
        raise RuntimeError

    def __getitem__(self, key):
        return self.__missing__(key)

    def __delitem__(self, key):
        raise RuntimeError

    def __iter__(self):
        raise RuntimeError

    def __len__(self):
        raise RuntimeError

    def __repr__(self):
        return f"< {self.__class__.__qualname__} for {self.elements!r} >"

    def __missing__(self, key):
        if isinstance(key, str):
            for elem in self.elements:
                if elem.p1.uid == key:
                    return (1, elem)
                elif elem.p2.uid == key:
                    return (2, elem)
            else:
                raise KeyError(f"{key!r}")
        elif isinstance(key, tuple):
            uid1, uid2 = key
            beginning_found = False
            elements = []
            for elem in self.elements:
                if (elem.p1.uid == uid1) or beginning_found:
                    elements.append(elem)
                    beginning_found = True
                if elem.p2.uid == uid2:
                    return elements
            else:
                raise KeyError(f"{key!r}")
        else:
            raise KeyError(f"{key!r}")

    @property
    def nelem(self):
        return len(self.elements)

    @property
    def nnodes(self):
        return self.nelem + 1

    def get_node_points(self):
        """
        """

        xyz = self.elements[0].p1.coord.reshape((1, 3))
        xyz = np.append(xyz, self.elements[0].p2.coord.reshape((1, 3)), axis=0)
        for elem in self.elements[1:]:
            xyz = np.append(xyz, elem.p2.coord.reshape((1, 3)), axis=0)
        return xyz

    def get_lims(self):
        xyz = self.get_node_points()
        x_max = np.max(xyz[:, 0])
        y_max = np.max(xyz[:, 1])
        z_max = np.max(xyz[:, 2])
        x_min = np.min(xyz[:, 0])
        y_min = np.min(xyz[:, 1])
        z_min = np.min(xyz[:, 2])
        return (x_min, x_max), (y_min, y_max), (z_min, z_max)
