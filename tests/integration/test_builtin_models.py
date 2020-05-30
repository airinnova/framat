#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from framat import Model


def test_cantilever():

    model = Model.example()
    model.run()

    model = Model.example('cantilever')
    model.run()
