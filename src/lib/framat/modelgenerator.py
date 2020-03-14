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
Frame model generator
"""

import uuid

import framat.fem.properties as props


STD_GRAV_ACCEL = 9.81


def get_uuid():
    """
    Return a (universally) unique identifier in a string representation

    Note:
        * This function uses UUID4,
          see https://en.wikipedia.org/wiki/Universally_unique_identifier
    """

    return str(uuid.uuid4())


class Model:

    def __init__(self):
        self.material = {}
        self.cross_section = {}
        self.beam = {}
        self.study = {}
        self.result = {}

    # ---------- Material ----------
    def add_material(self, uid):
        self.material[uid] = props.Material()

    def remove_material(self, uid):
        del self.material[uid]

    # ---------- Cross Section ----------
    def add_cross_section(self, uid):
        self.cross_section[uid] = props.CrossSection()

    def remove_cross_section(self, uid):
        del self.material[uid]

    # ---------- Beam ----------
    def add_beam(self, uid):
        pass

    def remove_beam(self, uid):
        del self.beam[uid]

    # ---------- Study ----------
    def add_study(self, uid):
        pass

    def remove_study(self, uid):
        del self.study[uid]

    # ---------- Result ----------
    def add_result(self, uid):
        pass

    def remove_result(self, uid):
        del self.result[uid]
