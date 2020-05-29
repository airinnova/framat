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
Run the model
"""

from . import MODULE_NAME
from . import _assembly as ass
from . import _meshing as mesh
from . import _plot as plot
from . import _solve as sol
from .__version__ import __version__
from ._log import logger


def run_model(m):
    """
    Run the complete model analysis

    Args:
        :m: instance of model
    """

    logger.info(f"===== {MODULE_NAME} {__version__} =====")

    # Instantiate result storage for each beam
    for mbeam in m.iter('beam'):
        m.results.add_feature('beam')

    # ----- MESHING -----
    logger.info("Meshing...")
    mesh.create_mesh(m)

    # ----- ASSEMBLING SYSTEM MATRICES -----
    logger.info("Assembling matrices...")
    # ass.get_mesh_stats(m)
    ass.create_system_matrices(m)
    ass.create_bc_matrices(m)

    # ----- SOLVING -----
    logger.info("Solving...")
    sol.solve(m)

    # ----- POST-PROCESSING -----
    logger.info("Post-processing...")
    plot.plot_all(m)
