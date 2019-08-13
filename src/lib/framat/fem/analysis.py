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
Analysis
"""

import numpy as np


def static_load_analysis(frame):
    """
    Perform a static load analysis

    Args:
        :frame: frame object

    Returns:
        :U: global vector of nodal displacements
        :F_react: reaction loads
    """

    K = frame.K
    B = frame.B
    F = frame.F
    F_accel = frame.F_accel
    b = frame.b
    ndof = frame.ndof

    # ===== Assemble the system of equations =====
    # Number of linear constraints
    n_lr = B.shape[0]
    Z = np.zeros((n_lr, n_lr))

    A_system = np.block([[K, B.T],
                         [B, Z]])
    x_system = np.block([[F + F_accel],
                         [b]])
    solution = np.linalg.solve(A_system, x_system)

    U = solution[0:ndof]
    F_react = solution[ndof:]
    return U, F_react


def free_vibration_analysis(frame):
    """
    Perform a free vibration analysis

    Args:
        :frame: frame object

    Returns:
        :U: global vector of nodal displacements
    """

    raise NotImplementedError("Vibration analysis is not yet implemented")
