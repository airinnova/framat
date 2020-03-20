#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test the PropertyHandler in the Python API
"""

import pytest

from framat.model import Material


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
