#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test the PropertyHandler in the Python API
"""

import pytest

from framat.model import Material, CrossSection


def test_material():
    """Test the Material class"""

    material = Material()
    material.set('E', 23)
    material.set('G', 55)
    material.set('rho', 2)

    assert material.get('E') == 23
    assert material.get('G') == 55
    assert material.get('rho') == 2

    with pytest.raises(KeyError):
        material.set('PROPERTY_DOES_NOT_EXIST', 1)


def test_cross_section():
    """Test the CrossSection class"""

    cross_section = CrossSection()
    cross_section.set('A', 23)
    cross_section.set('Iy', 55)
    cross_section.set('Iz', 2)

    assert cross_section.get('A') == 23
    assert cross_section.get('Iy') == 55
    assert cross_section.get('Iz') == 2

    with pytest.raises(KeyError):
        cross_section.set('PROPERTY_DOES_NOT_EXIST', 1)

