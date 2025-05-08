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
import scipy.sparse as sparse

from ._element import Element
from ._log import logger
from ._util import enumerate_with_step


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
    """
    Create system tensors K, M and F

    The stiffness matrix K and the mass matrix M are created as sparse matrices
    """

    r = m.results
    abm = m.results.get('mesh').get('abm')
    ndof_total = abm.ndofs()

    rows = empty(np.uint16)
    cols = empty(np.uint16)
    data_K = empty(np.float64)
    data_M = empty(np.float64)
    F = np.zeros((ndof_total, 1), dtype=np.float64)
    idx_start_beam = 0

    for i, mbeam in enumerate(m.iter('beam')):
        for k, abstr_elem in enumerate_with_step(abm.beams[i].values(), start=idx_start_beam, step=6):
            idxs = np.arange(k, k+12, 1, dtype=np.uint16)
            rows = np.append(rows, np.repeat(idxs, 12))
            cols = np.append(cols, np.tile(idxs, 12))

            phys_elem = Element.from_abstract_element(abstr_elem)
            data_K = np.append(
                data_K, phys_elem.stiffness_matrix_glob.flatten())
            data_M = np.append(data_M, phys_elem.mass_matrix_glob.flatten())
            F[k:k+12] += phys_elem.load_vector_glob

        idx_start_beam += abm.ndofs_beam(i)

    K = sparse_matrix(data_K, rows, cols)
    M = sparse_matrix(data_M, rows, cols)
    logger.info(
        f"System matrix size: {K.size} elements ({K.size/ndof_total**2:.2%} density)")

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
    pos_dict = {'ux': 0, 'uy': 1, 'uz': 2, 'thx': 3, 'thy': 4, 'thz': 5}

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


def sparse_matrix(data, rows, cols):
    """
    Return a compressed sparse matrix

    Duplicate entries are summed together
    """

    matrix = sparse.coo_matrix((data, (rows, cols)), dtype=np.float64)
    matrix = sparse.csr_matrix(matrix, dtype=np.float64)
    return matrix


def empty(dtype):
    return np.array([], dtype=dtype)
