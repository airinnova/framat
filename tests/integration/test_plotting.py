#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path

import pytest

from framat import Model
from framat._plot import PlotItems

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


def test_plotting():
    model = get_cantilever_model()

    pp = model.set_feature('post_proc')
    pp.set('plot_settings', {'save': '.', 'show': False})
    # Create two plots
    pp.add('plot', ['deformed', 'undeformed'])
    pp.add('plot', PlotItems.to_list())
    model.run()

    plot_files = model.results.get('files').get('plots')
    # Assert that two files have been created
    assert len(plot_files) == 2

    for fname in plot_files:
        assert fname.endswith('.png')
        fname = Path(fname)
        assert fname.is_file()
        os.remove(fname)
