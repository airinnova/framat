#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Copyright 2019 Airinnova AB and the FramAT authors
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
Interpolate
"""

from collections import namedtuple
from operator import attrgetter
import logging

import numpy as np

from framat.helpers.iterators import pairwise

logger = logging.getLogger(__name__)


class PointInterpolator:

    def __init__(self, points, point_uids=None):
        """
        Interpolate intermediate points for a list of points in space

        Args:
            :points: support points
        """

        # - at least two points should be given
        # - same points as input should not be allowed

        self.sup_points = [np.asarray(point) for point in points]
        self.point_uids = point_uids
        self.length = 0

        if self.point_uids is None:
            self.point_uids = [None for _ in range(len(self.sup_points))]

        self.interpol_table = []
        self._make_table = self._make_table()

    def __call__(self, xsi):
        """Shorthand for interpolate() method"""

        return self.interpolate(xsi)

    def _make_table(self):
        """
        Create a for interpolation

        Table contents:
            {support point} {relative position xsi}
        """

        self.interpol_table.append([self.sup_points[0], 0, self.point_uids[0]])

        idx = 1
        for p1, p2 in pairwise(self.sup_points):
            self.length += np.linalg.norm(p2 - p1)
            self.interpol_table.append([p2, self.length, self.point_uids[idx]])
            idx += 1

        for i in range(len(self.interpol_table)):
            self.interpol_table[i][1] /= self.length

    def get_xsi_support_points(self):
        """
        TODO
        """

        xsi = [row[:][1] for row in self.interpol_table]
        return xsi

    def interpolate(self, xsi):
        """
        Return a interpolated point at given xsi position

        Args:
            :xsi: relative position

        Returns:
            :point: interpolated point
        """

        if not 0 <= xsi <= 1:
            raise ValueError("xsi must be in range [0, 1]")

        for entry1, entry2 in pairwise(self.interpol_table):
            p1, xsi1, _ = entry1
            p2, xsi2, _ = entry2

            if xsi1 <= xsi <= xsi2:
                xsi -= xsi1
                xsi /= (xsi2 - xsi1)

                return p1 + xsi*(p2 - p1)

    def get_n_points(self, n, min_factor=0.1):
        """
        Return a list of :n: points

        Args:
            :n: number of points to return
        """

        if not 0 < min_factor <= 1:
            raise ValueError("min_factor must be in range (0, 1]")

        min_xsi_apart = min_factor*(1/n)

        InterPoint = namedtuple('InterPoint', ('coord', 'xsi', 'uid'))
        point_list = []

        xsi_with_uids = []
        for entry in self.interpol_table:
            p, xsi, uid = entry

            xsi_with_uids.append(xsi)

            new_point = InterPoint(coord=p, xsi=xsi, uid=uid)
            point_list.append(new_point)

        for xsi in np.linspace(0, 1, n):
            if xsi in {0, 1}:
                continue

            # Do not make a point if it is too close or equal to existing node position
            xsi_closest = min(xsi_with_uids, key=lambda x: abs(x - xsi))
            if abs(xsi_closest - xsi) < min_xsi_apart:
                logger.debug(f"Will not add xsi too close to existing: xsi = {xsi:.2e}, xsi_exists={xsi_closest:.2e}")
                continue

            new_point = InterPoint(coord=self.interpolate(xsi), xsi=xsi, uid=None)
            point_list.append(new_point)

        point_list = sorted(point_list, key=attrgetter('xsi'))
        return point_list


class PropertyInterpolator:

    def __init__(self, x, props):
        """
        Simple "next/previous" interpolator

        Args:
            :x: list of support points (strictly increasing)
            :props: list of properties (to interpolate between)
        """

        self.x = x
        self.props = props

        if len(self.x) != len(self.props):
            raise ValueError("x and props must be of same length")

        strictly_increasing = np.all(np.diff(self.x) > 0)
        if not strictly_increasing:
            raise ValueError("x must be strictly increasing")

    def interpolate(self, x, kind):
        """
        Interpolate property at given position x

        Notes:
            * The 'kind' parameter determines whether the next or previous
              property object shall be returned

        Args:
            :x: position at which to interpolate
            :kind: type of interpolation ('prev', 'next')

        Returns:
            :inperpol_property: interpolated property
        """

        if not (self.x[0] <= x <= self.x[-1]):
            raise ValueError("x is out of range")

        if kind not in ('prev', 'next'):
            raise ValueError("Invalid return type")

        for x_val, p_val in zip(pairwise(self.x), pairwise(self.props)):
            x1, x2 = x_val
            p1, p2 = p_val

            if x1 <= x <= x2:
                if kind == 'prev':
                    return p1
                else:
                    return p2

    def __call__(self, x, interpol_type):
        """Shorthand for interpolate() method"""

        return self.interpolate(x, interpol_type)
