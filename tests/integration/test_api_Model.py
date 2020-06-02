#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test the Python API
"""

import pytest

from framat import Model


# @pytest.mark.skip
def test_x():
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

    beam = model.add_feature('beam')
    beam.add('node', [0.0, 0, 0], uid='root1')
    beam.add('node', [0.5, 0, 0], uid='mid1')
    beam.add('node', [1.0, 0, 0], uid='tip1')
    beam.set('nelem', 10)
    beam.add('material', {'from': 'root1', 'to': 'tip1', 'uid': 'dummy'})
    beam.add('cross_section', {'from': 'root1', 'to': 'tip1', 'uid': 'dummy'})
    beam.add('orientation', {'from': 'root1', 'to': 'tip1', 'up': [0, 0, 1]})
    beam.add('point_load', {'at': 'tip1', 'load': [0, 0, -1, 0, 0, 0]})

    beam = model.add_feature('beam')
    beam.add('node', [0.0, 0, 1], uid='root2')
    beam.add('node', [0.5, 0, 1], uid='mid2')
    beam.add('node', [1.0, 0, 1], uid='tip2')
    beam.set('nelem', 40)
    beam.add('material', {'from': 'root2', 'to': 'tip2', 'uid': 'dummy'})
    beam.add('cross_section', {'from': 'root2', 'to': 'tip2', 'uid': 'dummy'})
    beam.add('orientation', {'from': 'root2', 'to': 'tip2', 'up': [0, 0, 1]})
    beam.add('point_load', {'at': 'tip2', 'load': [0, 0, -1, 0, 0, 0]})

    bc = model.set_feature('bc')
    bc.add('fix', {'node': 'root1', 'fix': ['all']})
    bc.add('fix', {'node': 'root2', 'fix': ['all']})

    r = model.run()

    # assert r.get('mesh').beams[0].get('named_node') == ['root1', 'mid1', 'tip1']
    # assert r.get('beam')[1].get('named_node') == ['root2', 'mid2', 'tip2']

    # assert r.get('mesh').get('global_nodes')[0]['eta'] == 0
    # assert r.get('mesh').get('global_nodes')[0]['coord'] == [0, 0, 0]
    # assert r.get('mesh').get('global_nodes')[2]['eta'] == 1
    # assert r.get('mesh').get('global_nodes')[2]['coord'] == [1, 0, 0]
    # assert r.get('mesh').get('global_nodes')[5]['eta'] == 1
    # assert r.get('mesh').get('global_nodes')[5]['coord'] == [1, 0, 1]


def test_builtin_cantilever():
    model = Model.example()
    model.run()
