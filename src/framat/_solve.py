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
Solving
"""

import numpy as np


def solve(m):
    static_load_analysis(m)

    # TODO : get deformation per beam

    U = m.results.get('tensors').get('U')
    beam = m.results.get('beam')[0]
    beam.set(
        'deformation',
        {
            'ux': U[0::6, ].flatten(),
            'uy': U[1::6, ].flatten(),
            'uz': U[2::6, ].flatten(),
            'thx': U[3::6, ].flatten(),
            'thy': U[4::6, ].flatten(),
            'thz': U[5::6, ].flatten(),
        },
    )


def static_load_analysis(m):
    """
    Perform a static load analysis

    Returns:
        :U: global vector of nodal displacements
        :F_react: reaction loads
    """

    mat = m.results.get('tensors')
    K = mat.get('K')
    B = mat.get('B')
    F = mat.get('F')

    ndof = K.shape[0]
    b = np.zeros((B.shape[0], 1))

    # ===== Assemble the system of equations =====
    # Number of linear constraints
    n_lr = B.shape[0]
    Z = np.zeros((n_lr, n_lr))

    A_system = np.block([
        [K, B.T],
        [B, Z]
    ])
    x_system = np.block([
        [F],  # + F_accel
        [b]
    ])
    solution = np.linalg.solve(A_system, x_system)

    U = solution[0:ndof]
    F_react = solution[ndof:]

    m.results.get('tensors').set('U', U)
    m.results.get('tensors').set('F_react', F_react)
