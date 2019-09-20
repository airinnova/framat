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
Save files
"""

import json
import logging

import numpy as np
from commonlibs.logger import truncate_filepath

logger = logging.getLogger(__name__)


def save_all(frame, save_results, filestructure):
    """
    Wrapper function that saves all results

    Args:
        :frame: frame object
        :save_results: settings
        :filestructure: file structure
    """

    if save_results.get('nodal_deformation', False):
        U = frame.deformation.U
        save_nodal_deformation(frame, U, filestructure)

    if save_results.get('mass_breakdown', False):
        save_mass_breakdown(frame, filestructure)

    if save_results.get('work_breakdown', False):
        save_work_breakdown(frame, filestructure)


def writejson(filename, output):
    """
    Write output to a JSON file with name 'filename'

    Args:
        :filename: file name as string
        :output: serializable object
    """

    with open(filename, 'w') as fp:
        json.dump(output, fp, indent=4, separators=(',', ': '))


def save_nodal_deformation(frame, U, filestructure):
    """
    Save nodal deformation to a JSON file

    Args:
        :frame: frame object
        :U: Global deformation vector
        :filestructure: file structure
    """

    filename = filestructure.files['results']['nodal_displacements']
    logger.info(f"Writing to file '{truncate_filepath(filename)}'")

    output = []
    for i in range(frame.counter.nodes):
        line = {
            "node_num": i,
            "uid": frame.finder.nodes.by_number[i].uid,
            "coord": list(frame.finder.nodes.by_number[i].coord),
            "deform": list(frame.deformation.by_node_num(i))
        }
        output.append(line)

    writejson(filename, output)


def save_nodal_reaction_loads(F_react, filestructure):
    """
    Save the nodal reaction loads to a JSON file

    Args:
        :F_react: vector containing the nodal reaction loads
        :filestructure: file structure
    """

    filename = filestructure.files['results']['nodal_reactions']
    logger.info(f"Writing to file '{truncate_filepath(filename)}'")

    # TODO: to be implemented
    pass


def save_mass_breakdown(frame, filestructure):
    """
    Save a mass breakdown of the frame structure to a JSON file

    Args:
        :frame: frame object
        :filestructure: file structure
    """

    filename = filestructure.files['results']['mass_breakdown']
    logger.info(f"Writing to file '{truncate_filepath(filename)}'")

    mass_breakdown = frame.get_mass_breakdown()
    writejson(filename, mass_breakdown)


def save_work_breakdown(frame, filestructure):
    """
    Save a work breakdown of the frame structure to a JSON file

    Args:
        :frame: frame object
        :filestructure: file structure
    """

    filename = filestructure.files['results']['work_breakdown']
    logger.info(f"Writing to file '{truncate_filepath(filename)}'")

    work_breakdown = frame.get_work_breakdown()
    writejson(filename, work_breakdown)
