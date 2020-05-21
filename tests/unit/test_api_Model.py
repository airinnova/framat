#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test the Python API
"""

import pytest

from framat import Model


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
    beam.set('nelem', 10)
    beam.add('node', {'uid': 'root', 'coord': [0, 0, 0]})
    beam.add('node', {'uid': 'tip', 'coord': [1, 0, 0]})
    beam.add('material', {'from': 'root', 'to': 'tip', 'uid': 'dummy'})
    beam.add('cross_section', {'from': 'root', 'to': 'tip', 'uid': 'dummy'})
    beam.add('orientation', {'from': 'root', 'to': 'tip', 'up': [0, 0, 1]})
    beam.add('load', {'at': 'tip', 'load': [0, 0, -1, 0, 0, 0]})

    model.run()
