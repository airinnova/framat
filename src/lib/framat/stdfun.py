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
Standard functions
"""

import logging
import os

import commonlibs.logger as hlogger

from framat.__version__ import __version__
from framat.fem.analysis import static_load_analysis, free_vibration_analysis
from framat.fem.frame import Frame
from framat.fem.properties import Materials, Profiles
import framat.fem.plot as plot
import framat.fileio.model as fmodel
import framat.fileio.save as save
import framat.fileio.utils as fu

logger = logging.getLogger(__name__)

__prog_name__ = 'framat'

DEFAULT_MODEL_FILENAME = f"{__prog_name__}_beam.json"


class StdRunArgs:

    def __init__(self, filename=None, verbose=False, debug=False,
                 quiet=False, no_schema_check=False, no_plots=False):
        """
        Arguments used in 'standard_run'

        Attributes:
            :filename: (str) Name of file to be loaded
            :verbose: (bool) If True, verbose logger setting
            :debug: (bool) If True, debug logger setting
            :quiet: (bool) If True, quiet logger setting
            :no_schema_check: (bool) If True, disable JSON schema validation
            :no_plots: (bool) If True, no plots will be generated
        """

        self.filename = filename
        self.verbose = verbose
        self.debug = debug
        self.quiet = quiet
        self.no_schema_check = no_schema_check
        self.no_plots = no_plots


def get_filestructure(filename, filecheck=True):
    """
    Get an instance of FileStructure()
    """

    return fu.FileStructure(os.path.abspath(filename), filecheck=filecheck)


def clean_project_dir(filestructure):
    """
    Remove old project files and directories
    """

    filestructure.clean()


def standard_run(args=None, filestructure=None, model=None):
    """
    Standard procedure

    Args:
        :args: arguments (see class 'StdRunArgs')
        :filestructure: file structure
    """

    # ===== Initialise =====
    filecheck = True
    if args is None:
        args = StdRunArgs()

    if args.filename is None:
        args.filename = DEFAULT_MODEL_FILENAME
        filecheck = False

    if filestructure is None:
        filestructure = get_filestructure(args.filename, filecheck)

    # TODO : MAKE BETTER
    if args.no_plots:
        make_plots = False
    else:
        make_plots = True

    # ===== Logging =====
    hlogger.init(filestructure.files['log'], level=args)
    logger = logging.getLogger(__name__)

    # ===== LOAD THE MODEL =====
    logger.info(hlogger.decorate(f"{__prog_name__} {__version__}"))

    if model is None:
        model = fmodel.load(filestructure.files['main'], validate_infile=args.no_schema_check)

    # ===== LOAD AND CREATE THE MODEL =====
    material_db = Materials.from_model_entry(model['materialdata'])
    profile_db = Profiles.from_model_entry(model['profildata'])

    frame = Frame(model['beamlines'],
                  model['boundary_conditions'],
                  model['acceleration'],
                  material_db, profile_db)

    # ===== SOLVE SYSTEM OF EQUATIONS =====
    analyses = model.get('analysis', None)
    if analyses.get('static', False):
        U, F_react = static_load_analysis(frame)
        frame.deformation.U = U

############################################################################
############################################################################
############################################################################
    # # --- Make possible to perform both analyses ----
    # if analyses.get('free_vibrations', False):
    #     U = free_vibration_analysis(frame)
    #     frame.deformation.U = U
############################################################################
############################################################################
############################################################################

    # ===== POSTPROCESSING =====
    # ----- Save results -----
    save_results = model.get('postproc', {}).get('save_results', False)
    if save_results:
        save.save_all(frame, save_results, filestructure)

    # ----- Create plots -----
    plots = model.get('postproc', {}).get('plots', False)
    if plots and make_plots:
        plot.plot_all(frame, plots, filestructure)

    # ===== RETURN DATA TO CALLER =====
    return_dict = {}
    return_dict['frame'] = frame
    return return_dict
