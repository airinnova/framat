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

from framat.fem.element import Element


def get_uuid():
    """
    Return a (universally) unique identifier in a string representation.
    This function uses UUID4 (https://en.wikipedia.org/wiki/Universally_unique_identifier).
    """
    return str(uuid.uuid4())


class PropertyHandler:
    """Meta class for handling model properties"""

    # TODO:
    # - Schema check of values to be set/added
    # - Define which properties can be set and which can be added (i.e. which are list-like!?)

    def __init__(self):
        self.props = {}
        self.allowed_keys = None
        self.allow_overwrite = True

    def set(self, key, value):
        """
        Attach a value to a property

        Args:
            :key: (str) name of the property to set
            :value: (any) value of the property
        """

        self._raise_error_if_key_not_allowed(key)
        self._raise_error_if_overwrite_not_allowed(key)
        self.props[key] = value

    def add(self, key, value):
        """
        Attach a value to a property list

        Args:
            :key: (str) name of the property to set
            :value: (any) value of the property
        """

        self._raise_error_if_key_not_allowed(key)
        self._append_prop_to_list(key, value)

    def get(self, key):
        return self.props[key]

    def iter(self, key):
        for value in self.props[key]:
            yield value

    def _raise_error_if_key_not_allowed(self, key):
        if self.allowed_keys and key not in self.allowed_keys:
            raise KeyError(f"Key '{key}' is not allowed")

    def _raise_error_if_overwrite_not_allowed(self, key):
        if not self.allow_overwrite and key in self.props.keys():
            raise KeyError(f"Property '{key}' is set and cannot be overwritten")

    def _append_prop_to_list(self, key, value):
        """
        Append a value to a property list

        Args:
            :key: (str) name of the property to set
            :value: (any) value of the property
        """

        if key not in self.props:
            self.props[key] = []
        elif not isinstance(self.props[key], list):
            raise ValueError
        self.props[key].append(value)


class Material(PropertyHandler):
    def __init__(self):
        super().__init__()
        self.allowed_keys = Element.MATERIAL_PROPS
        self.props = {key: 0 for key in self.allowed_keys}


class CrossSection(PropertyHandler):
    def __init__(self):
        super().__init__()
        self.allowed_keys = Element.CROSS_SECTION_PROPS
        self.props = {key: 0 for key in self.allowed_keys}


class Model:
    """
    The model object is a full description of the beam model to be analysed

    The system matrices will be derived from the model object
    """

    def __init__(self):
        self.material = {}
        self.cross_section = {}
        self.beam = {}
        self.study = {}

    # ---------- Material ----------
    def add_material(self, uid):
        self.material[uid] = Material()

    def remove_material(self, uid):
        del self.material[uid]

    # ---------- Cross Section ----------
    def add_cross_section(self, uid):
        self.cross_section[uid] = CrossSection()

    def remove_cross_section(self, uid):
        del self.cross_section[uid]

    # ---------- Beam ----------
    def add_beam(self, uid):
        self.beam[uid] = Beam()

    def remove_beam(self, uid):
        del self.beam[uid]

    # ---------- Study ----------
    def add_study(self, uid):
        self.study[uid] = None

    def remove_study(self, uid):
        del self.study[uid]

    # /// RESULTS SHOULD BE A CHILD OBJECT OF STUDY

# ======================================================================
# ======================================================================
# ======================================================================


class Beam:

    def __init__(self):
        self.props = {}
        self.props['nelem'] = 5
        self.props['node'] = []

    def set(self, prop, value):
        if prop == 'node':
            self._set_node(value)
        elif prop == 'nelem':
            self._set_node(value)
        elif prop == 'material':
            self._set_material(value)
        elif prop == 'cross_section':
            self._set_cross_section(value)

    def _set_node(self, value):
        self.props['node'].append(value)

    def _set_nelem(self, value):
        self.props['nelem'] = value

    def _cross_section(self, value):
        # self.props[''] = value
        ...
