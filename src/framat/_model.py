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

from mframework import FeatureSpec, ModelSpec

from ._run import run_model


class S:
    any_int = {'type': int}
    any_num = {'type': Number}
    pos_int = {'type': int, '>': 0}
    pos_number = {'type': Number, '>': 0}
    string = {'type': str, '>': 0}
    vector3x1 = {'type': list, 'min_len': 3, 'max_len': 3, 'item_types': Number}
    vector6x1 = {'type': list, 'min_len': 6, 'max_len': 6, 'item_types': Number}


# =================
# ===== MODEL =====
# =================
mspec = ModelSpec()

# ===== Material =====
fspec = FeatureSpec()
fspec.add_prop_spec(
    'uid',
    S.string,
    required=True,
    doc="Material UID"
)
fspec.add_prop_spec(
    'E',
    S.pos_number,
    required=True,
    doc="Young's modulus"
)
fspec.add_prop_spec(
    'G',
    S.pos_number,
    required=True,
    doc="Shear modulus"
)
fspec.add_prop_spec(
    'rho',
    S.pos_number,
    required=True,
    doc="Density"
)
mspec.add_feature_spec(
    'material',
    fspec,
    doc='Material properties'
)

# ===== Cross-section =====
fspec = FeatureSpec()
fspec.add_prop_spec(
    'uid',
    S.string,
    required=True,
    doc="Cross section UID"
)
fspec.add_prop_spec(
    'A',
    S.pos_number,
    required=True,
    doc="Area"
)
fspec.add_prop_spec(
    'Iy',
    S.pos_number,
    required=True,
    doc="Second moment of area about the local y-axis"
)
fspec.add_prop_spec(
    'Iz',
    S.pos_number,
    required=True,
    doc="Second moment of area about the local z-axis"
)
fspec.add_prop_spec(
    'J',
    S.pos_number,
    required=True,
    doc="Torsional constant"
)
mspec.add_feature_spec(
    'cross_section',
    fspec,
    required=False,
    doc='Cross-section properties'
)

# ===== Beam =====
fspec = FeatureSpec()
fspec.add_prop_spec(
    'node',
    {'$required_keys': ['uid', 'coord'], 'uid': S.string, 'coord': S.vector3x1},
    singleton=False,
    doc="Add a beam node"
)
fspec.add_prop_spec(
    'accel',
    {'$required_keys': ['direction'], 'direction': S.vector3x1, 'accel_factor': S.any_int},
    doc="Define a translational acceleration"
)
fspec.add_prop_spec(
    'orientation',
    {'$required_keys': ['from', 'to', 'up'], 'from': S.string, 'to': S.string, 'up': S.vector3x1},
    singleton=False,
    doc="Define the beam orientation"
)
fspec.add_prop_spec(
    'material',
    {'$required_keys': ['from', 'to', 'uid'], 'from': S.string, 'to': S.string, 'uid': S.string},
    singleton=False,
    doc="Add a material"
)
fspec.add_prop_spec(
    'cross_section',
    {'$required_keys': ['from', 'to', 'uid'], 'from': S.string, 'to': S.string, 'uid': S.string},
    singleton=False,
    doc="Add a cross section"
)
fspec.add_prop_spec(
    'load',
    {'$required_keys': ['at', 'load'], 'at': S.string, 'load': S.vector6x1},
    singleton=False,
    doc="Add a point load"
)
fspec.add_prop_spec(
    'mesh',
    {'$required_keys': ['from', 'to', 'nelem'], 'from': S.string, 'to': S.string, 'nelem': S.pos_int},
    singleton=False,
    doc="Specify the number nodes between to named nodes"
)
mspec.add_feature_spec(
    'beam',
    fspec,
    singleton=False,
    required=False,
    doc='Cross-section properties'
)

# ===== Boundary conditions =====
fspec = FeatureSpec()
fspec.add_prop_spec(
    'fix',
    {
        '$required_keys': ['node', 'fix'], 'node': S.string,
        'fix': {'type': list, 'min_len': 1, 'max_len': 6, 'item_types': str}
    },
    doc="Fix a beam node"
)
fspec.add_prop_spec(
    'connect',
    {
        '$required_keys': ['node1', 'node2', 'fix'], 'node1': S.string, 'node2': S.string,
        'fix': {'type': list, 'min_len': 1, 'max_len': 6, 'item_types': str}
    },
    doc="Connect two beam nodes"
)
mspec.add_feature_spec(
    'bc',
    fspec,
    singleton=True,
    required=True,
    doc='Cross-section properties'
)

# ===== Study =====
fspec = FeatureSpec()
fspec.add_prop_spec(
    'type',
    S.string,
    doc="Define a study type"
)
mspec.add_feature_spec('study', fspec, singleton=True, required=True, doc='Cross-section properties')

# ===== Post-proc =====
fspec = FeatureSpec()
fspec.add_prop_spec(
    'plot',
    {'$required_keys': ['args'], 'args': {'type': list, 'min_len': 1, 'item_types': dict}},
    doc="Add a plot"
)
mspec.add_feature_spec(
    'post_proc',
    fspec,
    singleton=True,
    required=True,
    doc='Cross-section properties'
)

# ===================
# ===== RESULTS =====
# ===================
rspec = ModelSpec()

# ===== Mesh =====
fspec = FeatureSpec()
fspec.add_prop_spec(
    'global_nodes',
    {'eta': S.any_num, 'coord': S.vector3x1},
    singleton=False,
    doc="Nodes (global system)"
)
fspec.add_prop_spec(
    'named_nodes',
    {'type': dict},
    singleton=True,
    doc="Mapping of named nodes to global node numbers"
)
rspec.add_feature_spec(
    'mesh',
    fspec,
    singleton=True,
    required=False,
    doc="Mesh"
)

# ===== Beam =====
fspec = FeatureSpec()
fspec.add_prop_spec(
    'named_node',
    S.string,
    singleton=False,
    doc="List of named nodes belonging to beam"
)
rspec.add_feature_spec(
    'beam',
    fspec,
    singleton=False,
    required=False,
    doc='Beam'
)

# ===== Deformation =====
fspec = FeatureSpec()
fspec.add_prop_spec(
    'max',
    S.pos_number,
    required=True,
    doc="Maximum deformation"
)
rspec.add_feature_spec(
    'deformation',
    fspec,
    doc='Deformation'
)

mspec.results = rspec


# ===== MODEL =====
class Model(mspec.user_class):
    def run(self):
        super().run()
        run_model(self)
        return self.results
