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
Meshing
"""

import itertools
import logging

import numpy as np

logger = logging.getLogger(__name__)


def pairwise(iterable):
    """
    Return a new iterator which yields pairwise items

    s --> (s0,s1), (s1,s2), (s2, s3), ...

    See: https://docs.python.org/3/library/itertools.html#itertools-recipes
    """

    a, b = itertools.tee(iterable)
    next(b, None)

    return zip(a, b)


class LineMesh:

    def __init__(self, sp):
        """
        Interpolate intermediate points for a list of points in space

        Args:
            :sp: (dict) support points (key: point UID, value: point)
        """

        # TODO: same points as input should not be allowed

        if len(sp) < 2:
            raise RuntimeError("need at least to points to create line mesh")

        # Support point coordinates and UIDs
        self.sp_coords = [np.array(p) for p in sp.values()]
        self.sp_uids = list(sp.keys())

        # Total line length
        self.len = 0

        # Intermediate table for interpolating points
        self.itab = []
        self._make_table()

    def __call__(self, eta):
        """Shorthand for 'interpolate()' method"""

        return self.interpolate(eta)

    def _make_table(self):
        """
        Create a table for point interpolation

        Table contents:
            | rel. coord. eta | abs. coord. | uid |
        """

        self.itab = []
        self.itab.append([0, self.sp_coords[0], self.sp_uids[0]])

        for i, (p1, p2) in enumerate(pairwise(self.sp_coords), start=1):
            dist = np.linalg.norm(p2 - p1)
            self.len += dist
            self.itab.append([self.len, p2, self.sp_uids[i]])

        for row in self.itab:
            row[0] /= self.len

    def interpolate(self, eta):
        """
        Return a interpolated point at given eta position

        Args:
            :eta: relative position

        Returns:
            :point: interpolated point
        """

        if not 0 <= eta <= 1:
            raise ValueError("xsi must be in range [0, 1]")

        for entry1, entry2 in pairwise(self.itab):
            p1, eta1, _ = entry1
            p2, eta2, _ = entry2

            if eta1 <= eta <= eta2:
                eta -= eta1
                eta /= (eta2 - eta1)

                return p1 + eta*(p2 - p1)

    def get_mesh(self, start_node=0):
        """
        TODO

        mesh:
            [
                {'eta': ..., 'coord': ...},
                {'eta': ..., 'coord': ...},
                ...
            ]

        named_nodes:
            {
                'uid1': 0,
                'uid2': 4,
                ...
            }
        """

        mesh = []
        named_nodes = {}
        for i, entry in enumerate(self.itab, start_node):
            eta, point, uid = entry
            mesh.append({'eta': eta, 'coord': point.tolist()})
            named_nodes[i] = uid

        return mesh, named_nodes
