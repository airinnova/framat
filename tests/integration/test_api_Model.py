#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test the Python API
"""

from mframework._log import disable_logger
disable_logger()

import pytest

from framat import Model


# @pytest.mark.skip
def test_x():
    model = Model()

    mat = model.set_feature('material')
    mat.set('uid', 'dummy')
    mat.set('E', 1)
    mat.set('G', 1)
    mat.set('rho', 1)

    cs = model.set_feature('cross_section')
    cs.set('uid', 'dummy')
    cs.set('A', 1)
    cs.set('Iy', 1)
    cs.set('Iz', 1)
    cs.set('J', 1)

    beam = model.add_feature('beam')
    beam.add('node', {'uid': 'root1', 'coord': [0, 0, 0]})
    beam.add('node', {'uid': 'mid1', 'coord': [0.5, 0, 0]})
    beam.add('node', {'uid': 'tip1', 'coord': [1, 0, 0]})
    beam.set('nelem', 10)
    beam.add('material', {'from': 'root1', 'to': 'tip1', 'uid': 'dummy1'})
    beam.add('cross_section', {'from': 'root1', 'to': 'tip1', 'uid': 'dummy'})
    beam.add('orientation', {'from': 'root1', 'to': 'tip1', 'up': [0, 0, 1]})
    beam.add('load', {'at': 'tip1', 'load': [0, 0, -1, 0, 0, 0]})

    beam = model.add_feature('beam')
    beam.add('node', {'uid': 'root2', 'coord': [0, 0, 1]})
    beam.add('node', {'uid': 'mid2', 'coord': [0.5, 0, 1]})
    beam.add('node', {'uid': 'tip2', 'coord': [1, 0, 1]})
    beam.set('nelem', 40)
    beam.add('material', {'from': 'root2', 'to': 'tip2', 'uid': 'dummy'})
    beam.add('cross_section', {'from': 'root2', 'to': 'tip2', 'uid': 'dummy'})
    beam.add('orientation', {'from': 'root2', 'to': 'tip2', 'up': [0, 0, 1]})
    beam.add('load', {'at': 'tip2', 'load': [0, 0, -1, 0, 0, 0]})

    r = model.run()

    assert r.get('beam')[0].get('named_node') == ['root1', 'mid1', 'tip1']
    assert r.get('beam')[1].get('named_node') == ['root2', 'mid2', 'tip2']

    # assert r.get('mesh').get('global_nodes')[0]['eta'] == 0
    # assert r.get('mesh').get('global_nodes')[0]['coord'] == [0, 0, 0]
    # assert r.get('mesh').get('global_nodes')[2]['eta'] == 1
    # assert r.get('mesh').get('global_nodes')[2]['coord'] == [1, 0, 0]
    # assert r.get('mesh').get('global_nodes')[5]['eta'] == 1
    # assert r.get('mesh').get('global_nodes')[5]['coord'] == [1, 0, 1]


def test_builtin_cantilever():
    model = Model.example()
    model.run()
