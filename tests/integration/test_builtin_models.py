#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test that the built-in example models can be run without errors
"""

import pytest

from framat import Model


def test_non_existent():
    with pytest.raises(ValueError):
        Model.example('MODEL_DOES_NOT_EXIST')


def test_cantilever():
    Model.example().run()
    Model.example('cantilever').run()


def test_helix():
    Model.example('helix').run()
