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
Boundary conditions
"""

import numpy as np


def connect(node1_number, node2_number, uid1, uid2, total_ndof, dof_constraints, frame):
    """
    Make a connection between two nodes

    Note:
        * The two nodes may belong to the same or to different beams

    Args:
        :node1_number: number of first node
        :node2_number: number of second node
        :uid1: UID of first node
        :uid2: UID of second node
        :total_ndof: total number of degrees of freedom
        :dof_constraints: list with dofs to be fixed (NOT YET IMPLEMENTED)
    """

    N1 = np.eye(6)
    N2 = -np.eye(6)

    x1 = frame.finder.nodes.by_uid[uid1].coord
    x2 = frame.finder.nodes.by_uid[uid2].coord
    x1 = np.asarray(x1)
    x2 = np.asarray(x2)
    dx, dy, dz = x1 - x2

    N2[0, 4] = -dz
    N2[0, 5] = dy
    N2[1, 3] = dz
    N2[1, 5] = -dx
    N2[2, 3] = -dy
    N2[2, 4] = dx

    B = np.zeros((6, frame.ndof))
    B[0:6, 6*node1_number:6*node1_number+6] = N1
    B[0:6, 6*node2_number:6*node2_number+6] = N2
    return B
