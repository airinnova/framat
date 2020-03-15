#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test the Python API
"""

from framat.model import Model


def test_model_attrs():
    """Test base attributes of the model object"""

    model = Model()
    assert hasattr(model, 'material')
    assert hasattr(model, 'cross_section')
    assert hasattr(model, 'beam')
    assert hasattr(model, 'study')


def test_adding_removing():
    """Test basic API adding and removing methods"""

    model = Model()
    model.add_material('steel')
    model.add_cross_section('I-section')
    model.add_beam('cantilever')
    model.add_study('static')

    model.remove_material('steel')
    model.remove_cross_section('I-section')
    model.remove_beam('cantilever')
    model.remove_study('static')
