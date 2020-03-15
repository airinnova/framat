#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test the Python API
"""

import pytest

from framat.model import Model


def test_model_attrs():
    model = Model()
    assert hasattr(model, 'material')
    assert hasattr(model, 'cross_section')
    assert hasattr(model, 'beam')
    assert hasattr(model, 'study')
    assert hasattr(model, 'result')


def test_material():
    model = Model()
    model.add_material('steel')
    model.material['steel'].set('E', 23)
    model.material['steel'].set('G', 55)
    model.material['steel'].set('rho', 2)

    assert model.material['steel'].get('E') == 23
    assert model.material['steel'].get('G') == 55
    assert model.material['steel'].get('rho') == 2

    with pytest.raises(KeyError):
        model.material['steel'].set('PROPERTY_DOES_NOT_EXIST', 1)

def test_cross_section():
    model = Model()
    model.add_cross_section('cs')
    model.cross_section['cs'].set('Iy', 23)

    assert model.cross_section['cs'].get('Iy') == 23

    with pytest.raises(KeyError):
        model.cross_section['cs'].set('PROPERTY_DOES_NOT_EXIST', 1)
