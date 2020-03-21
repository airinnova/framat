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

from numbers import Number

from commonlibs.model.model import PropertyHandler, get_uuid

from framat.fem.element import Element


class Material(PropertyHandler):
    def __init__(self):
        super().__init__()
        for prop in Element.MATERIAL_PROPS:
            self._add_prop_spec(prop, Number, is_required=True)


class CrossSection(PropertyHandler):
    def __init__(self):
        super().__init__()
        for prop in Element.CROSS_SECTION_PROPS:
            self._add_prop_spec(prop, Number, is_required=True)


class Beam(PropertyHandler):

    _SCHEMA_NODE = {
        '__REQUIRED_KEYS': ['uid', 'coord'],
        'uid': {'type': str},
        'coord': {'type': list, 'min_len': 3, 'max_len': 3, 'item_types': Number},
    }

    _SCHEMA_ACCELERATION = {
        '__REQUIRED_KEYS': ['direction'],
        'direction': {'type': list, 'min_len': 3, 'max_len': 3, 'item_types': Number},
        'accel_factor': {'type': int},
    }

    _SCHEMA_ORIENTATION = {
        '__REQUIRED_KEYS': ['from', 'to', 'up'],
        'from': {'type': str},
        'to': {'type': str},
        'up': {'type': list, 'min_len': 3, 'max_len': 3, 'item_types': Number},
    }

    _SCHEMA_MATERIAL = {
        '__REQUIRED_KEYS': ['from', 'to', 'uid'],
        'from': {'type': str},
        'to': {'type': str},
        'uid': {'type': str},
    }

    _SCHEMA_CROSS_SECTION = {
        '__REQUIRED_KEYS': ['from', 'to', 'uid'],
        'from': {'type': str},
        'to': {'type': str},
        'uid': {'type': str},
    }

    _SCHEMA_LOAD_POINT = {
        '__REQUIRED_KEYS': ['at', 'load'],
        'at': {'type': str},
        'load': {'type': list, 'min_len': 6, 'max_len': 6, 'item_types': Number},
    }

    def __init__(self):
        super().__init__()
        self._add_prop_spec('nelem', int)
        self._add_prop_spec('node', self._SCHEMA_NODE, is_listlike=True, is_required=True)
        self._add_prop_spec('acceleration', self._SCHEMA_ACCELERATION)
        self._add_prop_spec('orientation', self._SCHEMA_ORIENTATION, is_listlike=True)
        self._add_prop_spec('material', self._SCHEMA_MATERIAL, is_listlike=True)
        self._add_prop_spec('cross_section', self._SCHEMA_CROSS_SECTION, is_listlike=True)
        self._add_prop_spec('load', self._SCHEMA_LOAD_POINT, is_listlike=True)


class BoundaryCondition(PropertyHandler):

    _SCHEMA_FIX = {
        '__REQUIRED_KEYS': ['node', 'fix'],
        'node': {'type': str},
        'fix': {'type': list, 'min_len': 1, 'max_len': 6, 'item_types': str},
    }

    _SCHEMA_CONNECT = {
        '__REQUIRED_KEYS': ['node1', 'node2', 'fix'],
        'node1': {'type': str},
        'node2': {'type': str},
        'fix': {'type': list, 'min_len': 1, 'max_len': 6, 'item_types': str},
    }

    def __init__(self):
        super().__init__()
        self._add_prop_spec('fix', self._SCHEMA_FIX, is_listlike=True)
        self._add_prop_spec('connect', self._SCHEMA_CONNECT, is_listlike=True)


class Study(PropertyHandler):

    def __init__(self):
        super().__init__()
        self._add_prop_spec('type', str)


class Result(PropertyHandler):

    # TODO: extend schema!
    _SCHEMA_PLOT = {
        '__REQUIRED_KEYS': ['args'],
        'args': {'type': list, 'min_len': 1, 'item_types': dict},
    }

    def __init__(self):
        super().__init__()
        self._add_prop_spec('study', str, is_required=True)
        self._add_prop_spec('plot', self._SCHEMA_PLOT, is_listlike=True)


class Model:
    """
    The model object is a full description of the beam model to be analysed

    The system matrices will be derived from the model object
    """

    def __init__(self):
        self.material = {}
        self.cross_section = {}
        self.beam = {}
        self.boundary_condition = {}
        self.study = {}
        self.result = {}

    def add_material(self, uid=None):
        uid = self._set_uid(uid)
        self.material[uid] = Material()
        return uid

    def remove_material(self, uid):
        del self.material[uid]

    def add_cross_section(self, uid=None):
        uid = self._set_uid(uid)
        self.cross_section[uid] = CrossSection()
        return uid

    def remove_cross_section(self, uid):
        del self.cross_section[uid]

    def add_beam(self, uid=None):
        uid = self._set_uid(uid)
        self.beam[uid] = Beam()
        return uid

    def remove_beam(self, uid):
        del self.beam[uid]

    def add_boundary_condition(self, uid=None):
        uid = self._set_uid(uid)
        self.boundary_condition[uid] = BoundaryCondition()
        return uid

    def remove_boundary_condition(self, uid):
        del self.boundary_condition[uid]

    def add_study(self, uid=None):
        uid = self._set_uid(uid)
        self.study[uid] = Study()
        return uid

    def remove_study(self, uid):
        del self.study[uid]

    def add_result(self, uid=None):
        uid = self._set_uid(uid)
        self.result[uid] = Result()
        return uid

    def remove_result(self, uid):
        del self.result[uid]

    def _set_uid(self, uid):
        if uid is None:
            return get_uuid()
        if not isinstance(uid, str):
            raise ValueError(f"UID must be of type str, not {type(uid)}")
        else:
            return uid
