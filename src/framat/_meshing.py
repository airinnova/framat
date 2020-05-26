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

import logging
from math import ceil
from collections import OrderedDict

import numpy as np

from ._util import pairwise

logger = logging.getLogger(__name__)


def create_mesh(m):
    """Top-level function for mesh creation"""

    logger.info("Meshing...")

    r = m.results

    for i, (mbeam, rbeam) in enumerate(zip(m.iter('beam'), r.iter('beam'))):
        logger.info(f"Meshing beam with index {i}...")

        # Support points (= named nodes)
        sup_points = OrderedDict()
        for node in mbeam.iter('node'):
            # Collect the named nodes for each beam
            rbeam.add('named_node', node['uid'])
            sup_points[node['uid']] = node['coord']

        # Create a polygon line mesh for each beam
        mesh = LineMesh(sup_points, n=mbeam.get('nelem'))
        logger.info(f"Beam {i} has {len(mesh)} nodes")
        rbeam.set('mesh', mesh)


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


class Polygon:

    def __init__(self):
        self.segments = []
        self.len = 0

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


class LineMesh:

    def __init__(self, sup_points, n=6):
        """
        Geometric mesh
        """

        # Ensure that dictionary items are ordered correctly
        assert isinstance(sup_points, OrderedDict)
        assert isinstance(n, int)

        points = []
        for uid, coord in sup_points.items():
            points.append(Point(coord, rel_coord=None, uid=uid))

        segments = []
        for p1, p2 in pairwise(points):
            segments.append(LineSegment(p1, p2))

        self._polygon = Polygon()
        for seg in segments:
            self._polygon.add_segment(seg)

        # Create mesh points
        self._polygon.set_node_num(n)

    def __len__(self):
        return len(list(self._polygon.iter_points()))

    def iter_point_pairs(self):
        """
        Iterator for element point pairs

        Yields: (p1, p2)_1, (p1, p2)_2, ...
        """

        yield from pairwise(self._polygon.iter_points())
