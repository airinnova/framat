#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from framat import Model

REL_TOL = 1e-4


def get_cantilever_model():
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
    beam.add('node', [0, 0, 0], uid='root')
    beam.add('node', [1, 0, 0], uid='tip')
    beam.set('nelem', 10)
    beam.add('material', {'from': 'root', 'to': 'tip', 'uid': 'dummy'})
    beam.add('cross_section', {'from': 'root', 'to': 'tip', 'uid': 'dummy'})
    beam.add('orientation', {'from': 'root', 'to': 'tip', 'up': [0, 0, 1]})
    beam.add('point_load', {'at': 'tip', 'load': [0, 0, -1, 0, 0, 0]})

    model.set_feature('bc').add('fix', {'node': 'root', 'fix': ['all']})
    return model


def test_tip_force():
    model = get_cantilever_model()

    # Test tip deflection for different discretisations
    for nelem in (5, 17, 41, 83, 107):
        model.get('beam')[0].set('nelem', nelem)
        r = model.run()
        deform = r.get('tensors').get('comp:U')
        # Expected non-zero
        assert -1/3 == pytest.approx(deform['uz'][-1], rel=1e-4)
        assert 0.5 == pytest.approx(deform['thy'][-1], rel=REL_TOL)
        # Expected zero
        for p in ('ux', 'uy', 'thx', 'thz'):
            assert 0 == pytest.approx(deform[p][-1], rel=REL_TOL)
