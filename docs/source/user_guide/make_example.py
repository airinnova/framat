#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os
import shutil
import json
from pathlib import Path
import glob

from framat.stdfun import DEFAULT_MODEL_FILENAME

HERE = os.path.abspath(os.path.dirname(__file__))
MODEL_FILE = os.path.join(HERE, DEFAULT_MODEL_FILENAME)
MODEL_DIR_RESULTS = os.path.join(HERE, Path(MODEL_FILE).stem)
MODEL_DIR_RESULTS_PLOT = os.path.join(MODEL_DIR_RESULTS, 'plots')


def make_example():
    subprocess.run(["framat", "example", "-f", "-o", f"{DEFAULT_MODEL_FILENAME}"])


def run_analysis():
    subprocess.run(["framat", "run", f"{DEFAULT_MODEL_FILENAME}", "-cv"])


if __name__ == '__main__':
    path_before = os.getcwd()
    os.chdir(HERE)

    shutil.rmtree(MODEL_DIR_RESULTS, ignore_errors=True)
    make_example()

    with open(MODEL_FILE, 'r') as fp:
        model = json.load(fp)
    model['postproc']['plots'][0]['show'] = False
    with open(MODEL_FILE, 'w') as fp:
        json.dump(model, fp, indent=4, separators=(',', ': '))

    run_analysis()

    plot_files = glob.glob(os.path.join(MODEL_DIR_RESULTS_PLOT, '*'))
    shutil.copy(src=plot_files[0], dst=os.path.join(MODEL_DIR_RESULTS, '..', 'example.png'))

    os.chdir(path_before)
