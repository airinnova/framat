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
from .__version__ import __version__
from ._log import logger
from ._meshing import LineMesh


def run_model(m):
    """
    Run the complete model analysis

    Args:
        :model: instance of model
    """

    logger.info(f"===== {MODULE_NAME} {__version__} =====")
    logger.info(f"Number of beams: {m.len('beam')}")

    # ----- MESHING -----
    logger.info("Meshing...")
    mesh(m)

    # ----- ASSEMBLING SYSTEM MATRICES -----
    logger.info("Assembling matrices...")

    # ----- SOLVING -----
    logger.info("Solving...")

    # ----- POST-PROCESSING -----
    logger.info("Post-processing...")


def mesh(m):
    """Meshing"""

    r = m.results
    rmesh = r.set_feature('mesh')

    # Last global node number
    last_node_num = 0
    for i, mbeam in enumerate(m.iter('beam')):
        logger.info(f"Meshing beam with index {i}")
        rbeam = r.add_feature('beam')

        sup_points = {}
        for node in mbeam.iter('node'):
            rbeam.add('named_node', node['uid'])
            sup_points.update({node['uid']: node['coord']})

        mesh = LineMesh(sup_points)
        glob_nodes, named_node_map = mesh.get_mesh(start_node=last_node_num)
        rmesh.add('global_nodes', *glob_nodes)
        rmesh.set('named_nodes', named_node_map)
        last_node_num = rmesh.len('global_nodes') + 1
