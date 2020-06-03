#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def test_README_model():

    # =======================================================
    # KEEP SAME AS ON README PAGE
    # =======================================================

    from framat import Model

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
    beam.add('node', [1, 0, 0], uid='corner')
    beam.add('node', [1, 1, 0], uid='tip')
    beam.set('nelem', 10)
    beam.add('material', {'from': 'root', 'to': 'tip', 'uid': 'dummy'})
    beam.add('cross_section', {'from': 'root', 'to': 'tip', 'uid': 'dummy'})
    beam.add('orientation', {'from': 'root', 'to': 'tip', 'up': [0, 0, 1]})
    beam.add('point_load', {'at': 'corner', 'load': [0, 0, -1, 0, 0, 0]})

    bc = model.set_feature('bc')
    bc.add('fix', {'node': 'root', 'fix': ['all']})

    pp = model.set_feature('post_proc')
    # pp.add('plot', ('undeformed', 'deformed', 'nodes'))

    model.run()

    # =======================================================
    # =======================================================
    # =======================================================
