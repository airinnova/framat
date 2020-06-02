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
Model definition
"""

from uuid import uuid4

from mframework import FeatureSpec, ModelSpec, SchemadictValidators
import numpy as np

from ._meshing import AbstractBeamMesh
from ._run import run_model
from ._util import Schemas as S

# Register custom 'schemadict' types
SchemadictValidators.register_type(AbstractBeamMesh)
SchemadictValidators.register_type(np.ndarray)


# =================
# ===== MODEL =====
# =================
mspec = ModelSpec()

# ===== Material =====
fspec = FeatureSpec()
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
    singleton=False,
    required=False,
    doc='Material properties',
    uid_required=True,
)

# ===== Cross-section =====
fspec = FeatureSpec()
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
    singleton=False,
    required=False,
    doc='Cross-section properties',
    uid_required=True,
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
    'point_load',
    {'$required_keys': ['at', 'load'], 'at': S.string, 'load': S.vector6x1},
    singleton=False,
    doc="Add a point load"
)
fspec.add_prop_spec(
    'nelem',
    S.pos_int,
    singleton=True,
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
    singleton=False,
    doc="Fix a beam node"
)
fspec.add_prop_spec(
    'connect',
    {
        '$required_keys': ['node1', 'node2', 'fix'], 'node1': S.string, 'node2': S.string,
        'fix': {'type': list, 'min_len': 1, 'max_len': 6, 'item_types': str}
    },
    singleton=False,
    doc="Connect two beam nodes"
)
mspec.add_feature_spec(
    'bc',
    fspec,
    singleton=True,
    required=True,
    doc="Boundary conditions"
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
    'plot_settings',
    {
        'show': {'type', bool},
        'linewidth': S.pos_number,
        'markersize': S.pos_number,
        'fontsize': S.pos_int,
    },
    doc="General plot settings"
)
fspec.add_prop_spec(
    'plot',
    {
        'type': tuple,
        'allowed_items': (
            'deformed',
            'node_uids',
            'nodes',
            'undeformed',
        ),
    },
    singleton=False,
    doc="Add a geometry plot"
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
    'named_nodes',
    {'type': dict},
    singleton=True,
    doc="Mapping of named nodes to global node numbers"
)
fspec.add_prop_spec(
    'nbeam',
    S.pos_int,
    singleton=True,
    doc=""
)
fspec.add_prop_spec(
    'nelem',
    S.pos_int,
    singleton=True,
    doc=""
)
fspec.add_prop_spec(
    'nnode',
    S.pos_int,
    singleton=True,
    doc=""
)
fspec.add_prop_spec(
    'ndof',
    S.pos_int,
    singleton=True,
    doc=""
)
fspec.add_prop_spec(
    'abm',
    {'type': AbstractBeamMesh},
    singleton=True,
    doc=""
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
fspec.add_prop_spec(
    'mesh',
    {'type': AbstractBeamMesh},
    singleton=True,
    doc="List of named nodes belonging to beam"
)
fspec.add_prop_spec(
    'elements',
    {'type': list},
    singleton=True,
    doc="List of elements"
)
fspec.add_prop_spec(
    'deformation',
    {
        'ux': {'type': np.ndarray},
        'uy': {'type': np.ndarray},
        'uz': {'type': np.ndarray},
        'thx': {'type': np.ndarray},
        'thy': {'type': np.ndarray},
        'thz': {'type': np.ndarray},
    },
    singleton=True,
    doc="List of elements"
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
fspec.add_prop_spec('K', {'type': np.ndarray}, doc="TODO")
fspec.add_prop_spec('M', {'type': np.ndarray}, doc="TODO")
fspec.add_prop_spec('F', {'type': np.ndarray}, doc="TODO")
fspec.add_prop_spec('U', {'type': np.ndarray}, doc="TODO")
fspec.add_prop_spec('B', {'type': np.ndarray}, doc="TODO")
fspec.add_prop_spec('F_react', {'type': np.ndarray}, doc="TODO")
rspec.add_feature_spec(
    'matrices',
    fspec,
    singleton=True,
    doc='System matrices'
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

    @classmethod
    def example(cls, example='cantilever'):
        if example == 'cantilever':
            return get_example_cantilever()
        elif example == 'helix':
            return get_example_helix()
        else:
            raise ValueError('unknown model: {example!r}')


def init_examples():
    model = Model()
    mat = model.add_feature('material', uid='dummy')
    mat.set('E', 1)
    mat.set('G', 1)
    mat.set('rho', 1)

    cs = model.add_feature('cross_section', uid='dummy')
    cs.set('A', 1)
    cs.set('Iy', 1)
    cs.set('Iz', 1)
    cs.set('J', 1)
    return model


def get_example_cantilever():
    model = init_examples()

    beam = model.add_feature('beam')
    beam.add('node', {'uid': 'root', 'coord': [0, 0, 0]})
    beam.add('node', {'uid': 'tip', 'coord': [1, 0, 0]})
    beam.set('nelem', 10)
    beam.add('material', {'from': 'root', 'to': 'tip', 'uid': 'dummy'})
    beam.add('cross_section', {'from': 'root', 'to': 'tip', 'uid': 'dummy'})
    beam.add('orientation', {'from': 'root', 'to': 'tip', 'up': [0, 0, 1]})
    beam.add('point_load', {'at': 'tip', 'load': [0, 0, -1, 0, 0, 0]})

    bc = model.set_feature('bc')
    bc.add('fix', {'node': 'root', 'fix': ['all']})
    return model


def get_example_helix():
    model = init_examples()

    model.get('material')[0].set('E', 1e5)
    model.get('material')[0].set('G', 1e4)

    def helix(a, b, c, t):
        """
        Make a Helix
        See: https://en.wikipedia.org/wiki/Helix
        """

        x = a*np.cos(t)
        y = b*np.sin(t)
        z = c*t
        return (x, y, z)

    # Generate node coordinates
    t = np.linspace(0, 20, num=200)
    x, y, z = helix(a=10, b=5, c=0.5, t=t)

    beam = model.add_feature('beam')
    for x_coord, y_coord, z_coord in zip(x, y, z):
        beam.add('node', {'uid': str(uuid4()), 'coord': [x_coord, y_coord, z_coord]})

    first_uid = beam.get('node')[0]['uid']
    last_uid = beam.get('node')[-1]['uid']

    beam.set('nelem', 1)
    beam.add('material', {'from': first_uid, 'to': last_uid, 'uid': 'dummy'})
    beam.add('cross_section', {'from': first_uid, 'to': last_uid, 'uid': 'dummy'})
    beam.add('orientation', {'from': first_uid, 'to': last_uid, 'up': [0, 0, 1]})
    beam.add('point_load', {'at': last_uid, 'load': [0, 0, -1, 0, 0, 0]})

    bc = model.set_feature('bc')
    bc.add('fix', {'node': first_uid, 'fix': ['all']})
    return model
