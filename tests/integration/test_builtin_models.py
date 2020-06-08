#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test that the built-in example models can be run without errors
"""

import pytest

from framat import Model


def test_non_existent():
    with pytest.raises(ValueError):
        Model.from_example('MODEL_DOES_NOT_EXIST')


def test_cantilever():
    Model.from_example().run()
    Model.from_example('cantilever').run()


def test_helix():
    Model.from_example('helix').run()
