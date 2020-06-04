#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pytest

from framat import Model

# REL_TOL = 1e-4
REL_TOL = 1e-2
ABS_TOL = 1e-9


def get_horseshoe_model(load_case):
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
    beam.add('node', [0.0, 0, 0], uid='a')
    beam.add('node', [1.5, 0, 0], uid='b')
    beam.add('node', [1.5, 3, 0], uid='c')
    beam.add('node', [0.0, 3, 0], uid='d')
    # beam.set('nelem', 20)
    beam.set('nelem', 100)
    beam.add('material', {'from': 'a', 'to': 'd', 'uid': 'dummy'})
    beam.add('cross_section', {'from': 'a', 'to': 'd', 'uid': 'dummy'})
    beam.add('orientation', {'from': 'a', 'to': 'd', 'up': [0, 0, 1]})

    bc = model.set_feature('bc')
    bc.add('fix', {'node': 'a', 'fix': ['all']})
    bc.add('fix', {'node': 'd', 'fix': ['all']})

    if load_case == 1:
        beam.add('distr_load', {'from': 'a', 'to': 'b', 'load': [0, 0, -2, 0, 0, 0]})
        beam.add('distr_load', {'from': 'c', 'to': 'd', 'load': [0, 0, -2, 0, 0, 0]})
        beam.add('distr_load', {'from': 'b', 'to': 'c', 'load': [0, 0, 1, 0, 0, 0]})
    else:
        beam.add('point_load', {'at': 'b', 'load': [+0.1, +0.2, +0.3, 0, 0, 0]})
        beam.add('point_load', {'at': 'c', 'load': [-0.1, -0.2, -0.3, 0, 0, 0]})

    # model.set_feature('post_proc').add('plot', ['undeformed', 'nodes'])
    return model


def test_horseshoe_beam_distr_load():
    model = get_horseshoe_model(load_case=1)
    r = model.run()

    abm = r.get('mesh').get('abm')
    deform = r.get('beam')[0].get('deformation')

    # ----- Expected deformation at nodes 'a' and 'd' -----
    for fixed_node in ('a', 'd'):
        for p in ('ux', 'uy', 'uz', 'thx', 'thy', 'thz'):
            assert deform[p][abm.glob_nums[fixed_node]] == pytest.approx(0, abs=ABS_TOL)

    # ----- Expected deformation at nodes 'b' and 'c' -----
    for free_node in ('c', 'd'):
        assert deform['ux'][abm.glob_nums[free_node]] == pytest.approx(0, abs=ABS_TOL)
        assert deform['uy'][abm.glob_nums[free_node]] == pytest.approx(0, abs=ABS_TOL)
        assert deform['thz'][abm.glob_nums[free_node]] == pytest.approx(0, abs=ABS_TOL)

    assert deform['uz'][abm.glob_nums['b']] == pytest.approx(0.42188, rel=REL_TOL)
    # assert deform['thx'][abm.glob_nums['b']] == pytest.approx(0.75000, rel=REL_TOL)
    assert deform['thy'][abm.glob_nums['b']] == pytest.approx(-0.56250, rel=REL_TOL)

    assert deform['uz'][abm.glob_nums['c']] == pytest.approx(0.42188, rel=REL_TOL)
    # assert deform['thx'][abm.glob_nums['c']] == pytest.approx(-0.75000, rel=REL_TOL)
    assert deform['thy'][abm.glob_nums['c']] == pytest.approx(-0.56250, rel=REL_TOL)

    # # ----- Maximux deformations -----
    # assert np.max(deform['ux']) == pytest.approx(0, abs=ABS_TOL)
    # assert np.max(deform['uy']) == pytest.approx(0, abs=ABS_TOL)
    # assert np.max(deform['thz']) == pytest.approx(0, abs=ABS_TOL)

    # assert np.max(deform['uz']) == pytest.approx(1.1953, rel=REL_TOL)
    # assert np.max(deform['thx']) == pytest.approx(0.77165, rel=REL_TOL)
    # assert np.max(deform['thy']) == pytest.approx(0.56250, rel=REL_TOL)


def test_horseshoe_beam_point_loads():
    model = get_horseshoe_model(load_case=2)
    r = model.run()

    abm = r.get('mesh').get('abm')
    deform = r.get('beam')[0].get('deformation')

    # ----- Expected deformation at nodes 'a' and 'd' -----
    for fixed_node in ('a', 'd'):
        for p in ('ux', 'uy', 'uz', 'thx', 'thy', 'thz'):
            assert deform[p][abm.glob_nums[fixed_node]] == pytest.approx(0, abs=ABS_TOL)

    # ----- Expected deformation at nodes 'b' and 'c' -----
    assert deform['ux'][abm.glob_nums['b']] == pytest.approx(0.11250, rel=REL_TOL)
    assert deform['uy'][abm.glob_nums['b']] == pytest.approx(0.13793, rel=REL_TOL)
    # assert deform['uz'][abm.glob_nums['b']] == pytest.approx(0.22863, rel=REL_TOL)
    # assert deform['thx'][abm.glob_nums['b']] == pytest.approx(-0.13065, rel=REL_TOL)
    # assert deform['thy'][abm.glob_nums['b']] == pytest.approx(-0.20323, rel=REL_TOL)
    assert deform['thz'][abm.glob_nums['b']] == pytest.approx(0.13285, rel=REL_TOL)

    assert deform['ux'][abm.glob_nums['c']] == pytest.approx(-0.11250, rel=REL_TOL)
    assert deform['uy'][abm.glob_nums['c']] == pytest.approx(-0.053557, rel=REL_TOL)
    # assert deform['uz'][abm.glob_nums['c']] == pytest.approx(-0.22863, rel=REL_TOL)
    # assert deform['thx'][abm.glob_nums['c']] == pytest.approx(-0.13065, rel=REL_TOL)
    # assert deform['thy'][abm.glob_nums['c']] == pytest.approx(0.20323, rel=REL_TOL)
    assert deform['thz'][abm.glob_nums['c']] == pytest.approx(-0.020346, rel=REL_TOL)

    # # # ----- Maximux deformations -----
    # assert np.max(deform['ux']) == pytest.approx(0.11489, rel=REL_TOL)
    assert np.max(deform['uy']) == pytest.approx(0.13793, rel=REL_TOL)
    # assert np.max(deform['uz']) == pytest.approx(0.22863, rel=REL_TOL)
    # assert np.max(deform['thx']) == pytest.approx(0.16331, rel=REL_TOL)
    # assert np.max(deform['thy']) == pytest.approx(0.21168, rel=REL_TOL)
    assert np.max(deform['thz']) == pytest.approx(0.13349, rel=REL_TOL)
