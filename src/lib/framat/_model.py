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


class Schema:
    positive_int = {'type': int, '>': 0}
    positive_number = {'type': Number, '>': 0}
    string = {'type': str, '>': 0}

    class beam:
        node = {
            '$required_keys': ['uid', 'coord'],
            'uid': {'type': str},
            'coord': {'type': list, 'min_len': 3, 'max_len': 3, 'item_types': Number},
        }
        accel = {
            '$required_keys': ['direction'],
            'direction': {'type': list, 'min_len': 3, 'max_len': 3, 'item_types': Number},
            'accel_factor': {'type': int},
        }
        orientation = {
            '$required_keys': ['from', 'to', 'up'],
            'from': {'type': str},
            'to': {'type': str},
            'up': {'type': list, 'min_len': 3, 'max_len': 3, 'item_types': Number},
        }
        material = {
            '$required_keys': ['from', 'to', 'uid'],
            'from': {'type': str},
            'to': {'type': str},
            'uid': {'type': str},
        }
        cross_section = {
            '$required_keys': ['from', 'to', 'uid'],
            'from': {'type': str},
            'to': {'type': str},
            'uid': {'type': str},
        }
        load_point = {
            '$required_keys': ['at', 'load'],
            'at': {'type': str},
            'load': {'type': list, 'min_len': 6, 'max_len': 6, 'item_types': Number},
        }

    class bc:
        fix = {
            '$required_keys': ['node', 'fix'],
            'node': {'type': str},
            'fix': {'type': list, 'min_len': 1, 'max_len': 6, 'item_types': str},
        }
        connect = {
            '$required_keys': ['node1', 'node2', 'fix'],
            'node1': {'type': str},
            'node2': {'type': str},
            'fix': {'type': list, 'min_len': 1, 'max_len': 6, 'item_types': str},
        }

    class pp:
        plot = {
            '$required_keys': ['args'],
            'args': {'type': list, 'min_len': 1, 'item_types': dict},
        }


mspec = ModelSpec()

# ===== Material =====
fspec = FeatureSpec()
fspec.add_item_spec('E', Schema.positive_number, required=True, doc="Young's modulus")
fspec.add_item_spec('G', Schema.positive_number, required=True, doc="Shear modulus")
fspec.add_item_spec('rho', Schema.positive_number, required=True, doc="Density")
mspec.add_feature_spec('material', fspec, doc='Material properties')

# ===== Cross-section =====
fspec = FeatureSpec()
fspec.add_item_spec('A', Schema.positive_number, required=True, doc="Area")
fspec.add_item_spec('Iy', Schema.positive_number, required=True, doc="Second moment of area about the local y-axis")
fspec.add_item_spec('Iz', Schema.positive_number, required=True, doc="Second moment of area about the local z-axis")
fspec.add_item_spec('J', Schema.positive_number, required=True, doc="Torsional constant")
mspec.add_feature_spec('cross_section', fspec, required=False, doc='Cross-section properties')

# ===== Beam =====
fspec = FeatureSpec()
fspec.add_item_spec('nelem', Schema.positive_int, doc="Number of beam elements")
fspec.add_item_spec('node', Schema.beam.node, doc="Add a beam node")
fspec.add_item_spec('accel', Schema.beam.accel, doc="Define a translational acceleration")
fspec.add_item_spec('orientation', Schema.beam.orientation, doc="Define the beam orientation")
fspec.add_item_spec('material', Schema.beam.material, doc="Add a material")
fspec.add_item_spec('cross_section', Schema.beam.cross_section, doc="Add a cross section")
fspec.add_item_spec('load', Schema.beam.load_point, doc="Add a point load")
mspec.add_feature_spec('beam', fspec, singleton=False, required=False, doc='Cross-section properties')

# ===== Boundary conditions =====
fspec = FeatureSpec()
fspec.add_item_spec('fix', Schema.bc.fix, doc="Fix a beam node")
fspec.add_item_spec('bc', Schema.bc.connect, doc="Connect two beam nodes")
mspec.add_feature_spec('bc', fspec, singleton=True, required=True, doc='Cross-section properties')

# ===== Study =====
fspec = FeatureSpec()
fspec.add_item_spec('type', Schema.string, doc="Define a study type")
mspec.add_feature_spec('study', fspec, singleton=True, required=True, doc='Cross-section properties')

# ===== Post-proc =====
fspec = FeatureSpec()
fspec.add_item_spec('plot', Schema.pp.plot, doc="Add a plot")
mspec.add_feature_spec('post_proc', fspec, singleton=True, required=True, doc='Cross-section properties')


# ===== MODEL =====
class Model(mspec.user_class):
    def run(self):
        super().run()
        run_model(self)


if __name__ == '__main__':
    from mframework import doc2rst
    print(doc2rst(mspec.get_docs()))
