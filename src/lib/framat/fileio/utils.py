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
File paths
"""

import os
import shutil
from datetime import datetime

DIR_PLOT = 'plots'
DIR_RESULTS = 'results'


class FileStructure:

    def __init__(self, infile, make_dirs=True, filecheck=True):
        """
        Keep dictionaries of files and directories
        """

        # Make filepath absolute
        infile = os.path.abspath(infile)

        if filecheck and not os.path.isfile(infile):
            raise IOError(f"'{infile} is not a valid input file'")

        self.basename = os.path.splitext(os.path.basename(infile))[0]
        self.dirname = os.path.dirname(infile)

        self.files = {
            "main": infile,
            "log": os.path.join(self.dirname, self.basename, 'log.txt'),
            "results": {
                "nodal_displacements": os.path.join(self.dirname, self.basename, DIR_RESULTS, "nodal_displacements.json"),
                "nodal_reactions": os.path.join(self.dirname, self.basename, DIR_RESULTS, "nodal_reactions.json"),
                "mass_breakdown": os.path.join(self.dirname, self.basename, DIR_RESULTS, "mass_breakdown.json"),
                "work_breakdown": os.path.join(self.dirname, self.basename, DIR_RESULTS, "work_breakdown.json"),
                }
            }

        self.dirs = {
            "project_results": os.path.join(self.dirname, self.basename),
            "results": os.path.join(self.dirname, self.basename, DIR_RESULTS),
            "plots": os.path.join(self.dirname, self.basename, DIR_PLOT),
        }

        if make_dirs:
            self.make_dirs()

    def make_dirs(self):
        """
        Make project directories
        """

        for dirpath in self.dirs.values():
            makedir(dirpath)

    def clean(self):
        """
        Remove old result files
        """

        shutil.rmtree(self.dirs['project_results'], ignore_errors=True)


def makedir(dirname):
    """
    Make a directory and return the absolute path
    """

    abspath = os.path.abspath(dirname)

    if not os.path.exists(abspath):
        os.makedirs(abspath)

    return abspath


def join2abs(*args):
    """
    Combine path name components and return the absoulute path name

    Takes same arguments as 'os.path.join()'
    """

    return os.path.abspath(os.path.join(*args))


def get_date_str():
    """
    Return a date string
    """

    now = datetime.now().strftime("%F_%H-%M-%S-%f")
    return now
