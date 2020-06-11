#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path

# Suppress Matplotlib figure
from matplotlib import pyplot as plt
import matplotlib
plt.ioff()
matplotlib.use('Agg')

HERE = os.path.abspath(os.path.dirname(__file__))
TARGET = os.path.join(HERE, 'getting_started_models')


def rerun_and_save_plots(model, fname):
    old_ps = model.get('post_proc').get('plot_settings')
    model.get('post_proc').set('plot_settings', {**old_ps, 'save': TARGET})
    r = model.run()

    old_fname = Path(r.get('files').get('plots')[0])
    new_fname = os.path.join(os.path.dirname(old_fname), fname)
    os.rename(old_fname, new_fname)


def test_cantilever():
    from getting_started_models import example_cantilever as M
    rerun_and_save_plots(M.model, fname='example_cantilever.png')

def test_model2():
    from getting_started_models import example_model2 as M
    rerun_and_save_plots(M.model, fname='example_model2.png')
