#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Suppress Matplotlib figure
from matplotlib import pyplot as plt
import matplotlib
plt.ioff()
matplotlib.use('Agg')


def test_cantilever():
    from getting_started_models import _doc_cantilever

def test_model2():
    from getting_started_models import _doc_model2
