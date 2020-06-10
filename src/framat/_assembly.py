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
Assembly
"""

import numpy as np

from ._util import enumerate_with_step
from ._element import Element

# TODO: use sparse matrices


def create_system_matrices(m):
    """
    Assemble global tensors

        * :K: global stiffness matrix
        * :M: global mass matrix
        * :F: global load vector
        * :B: constraint matrix
    """

    create_main_tensors(m)
    create_bc_matrices(m)


def create_main_tensors(m):
    """Create K, M and F"""

    r = m.results
    abm = m.results.get('mesh').get('abm')

    # Create a stiffness matrix for each beam
    K_per_beam = []
    M_per_beam = []
    F_per_beam = []
    for i, mbeam in enumerate(m.iter('beam')):
        ndof_beam = abm.ndofs_beam(i)
        K_beam = np.zeros((ndof_beam, ndof_beam))
        M_beam = np.zeros((ndof_beam, ndof_beam))
        F_beam = np.zeros((ndof_beam, 1))

        for k, abstr_elem in enumerate_with_step(abm.beams[i].values(), step=6):
            phys_elem = Element.from_abstract_element(abstr_elem)
            K_beam[k:k+12, k:k+12] += phys_elem.stiffness_matrix_glob
            M_beam[k:k+12, k:k+12] += phys_elem.mass_matrix_glob
            F_beam[k:k+12] += phys_elem.load_vector_glob

        K_per_beam.append(K_beam)
        M_per_beam.append(M_beam)
        F_per_beam.append(F_beam)

    ndof_total = abm.ndofs()
    K = np.zeros((ndof_total, ndof_total))
    M = np.zeros((ndof_total, ndof_total))
    F = np.zeros((ndof_total, 1))

    # Paste each beam tensor into the global tensor
    paste_range = [0, 0]
    for K_beam, M_beam, F_beam in zip(K_per_beam, M_per_beam, F_per_beam):
        rx = K_beam.shape[0]
        from_r = paste_range[1]
        to_r = from_r + rx
        paste_range = [from_r, to_r]
        K[from_r:to_r, from_r:to_r] = K_beam
        M[from_r:to_r, from_r:to_r] = M_beam
        F[from_r:to_r] += F_beam

    rtensors = r.set_feature('tensors')
    rtensors.set('K', K)
    rtensors.set('M', M)
    rtensors.set('F', F)


def create_bc_matrices(m):
    """Assemble the constraint matrix B"""

    r = m.results
    abm = r.get('mesh').get('abm')
    ndofs = abm.ndofs()
    mbc = m.get('bc')

    B_tot = np.array([])
    # ----- Fix DOFs -----
    for fix in mbc.iter('fix'):
        num_node = abm.glob_nums[fix['node']]
        B = fix_dof(num_node, ndofs, fix['fix'])
        B_tot = np.vstack((B_tot, B)) if B_tot.size else B

    # ----- Multipoint constraints (MPC) -----
    for con in mbc.iter('connect'):
        uid1, uid2 = con['node1'], con['node2']
        num_node1 = abm.glob_nums[uid1]
        num_node2 = abm.glob_nums[uid2]
        x1 = abm.get_point_by_uid(uid1)
        x2 = abm.get_point_by_uid(uid2)
        B = connect(x1, x2, num_node1, num_node2, ndofs, con['fix'])
        B_tot = np.vstack((B_tot, B)) if B_tot.size else B

    m.results.get('tensors').set('B', B_tot)


def fix_dof(node_number, total_ndof, dof_constraints):
    """
    Return part of constraint matrix B for fixed degrees of freedom

    Note:
        * Only non-zero rows are returned. If, say, three dof are fixed, then
          B will have size 3xndof

    Args:
        :node_number: node_number
        :total_ndof: total number of degrees of freedom
        :dof_constraints: list with dofs to be fixed
    """

    B = np.array([])
    pos_dict = {'ux': 0, 'uy': 1, 'uz': 2, 'tx': 3, 'ty': 4, 'tz': 5}

    for constraint in dof_constraints:
        if constraint == 'all':
            B = np.zeros((6, total_ndof))
            B[0:6, 6*node_number:6*node_number+6] = np.eye(6)
            break
        else:
            pos = pos_dict[constraint]

            B_row = np.zeros((1, total_ndof))
            B_row[0, 6*node_number+pos] = 1
            B = np.vstack((B, B_row)) if B.size else B_row

    return B


def connect(x1, x2, num_node1, num_node2, ndofs, dof_constraints):
    """
    Make a rigid connection between two nodes

    Note:
        * The two nodes may belong to the same or to different beams

    Args:
        :x1: (numpy) coordinate of point 1
        :x2: (numpy) coordinate of point 2
        :num_node1: (int) global node number of point 1
        :num_node2: (int) global node number of point 2
        :ndofs: (int) number of dofs
        :dof_constraints: list with dofs to be fixed (NOT YET IMPLEMENTED)
    """

    dx, dy, dz = x1 - x2

    N1 = np.eye(6)
    N2 = -np.eye(6)

    N2[0, 4] = -dz
    N2[0, 5] = dy
    N2[1, 3] = dz
    N2[1, 5] = -dx
    N2[2, 3] = -dy
    N2[2, 4] = dx

    B = np.zeros((6, ndofs))
    B[0:6, 6*num_node1:6*num_node1+6] = N1
    B[0:6, 6*num_node2:6*num_node2+6] = N2
    return B
