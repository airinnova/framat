#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
from contextlib import contextmanager
import uuid
import shutil
from pathlib import Path

from framat.stdfun import DEFAULT_MODEL_FILENAME

BIN_NAME = 'framat'


@contextmanager
def clean_run(file_name, rm_dir=True):
    """
    Remove file with name 'file_name' if it exists and also remove it at the end

    Note:

        * If 'file_name' is 'testing.json' 'rm_dir' is True,
          a directory with name 'testing' will also be removed.

    Args:
        :file_name: (str) File name
        :rm_dir: (bool) Flag
    """

    def rm_file(fname):
        if os.path.exists(fname):
            os.remove(fname)

    rm_file(file_name)
    try:
        yield file_name
    finally:
        rm_file(file_name)

        if rm_dir:
            shutil.rmtree(Path(file_name).stem, ignore_errors=True)


def which(program):
    """
    Emulate 'which'

    See:

    https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    """

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def test_bin_exists():
    """
    Test that main executable exists and is executable
    """

    assert which(f'{BIN_NAME}') is not None

    # Just make sure this runs without error
    os.system(f'{BIN_NAME} -h')
    os.system(f'{BIN_NAME} --help')


def test_mode_example():
    """
    Test 'example' mode
    """

    # ----- Standard file name -----
    with clean_run(DEFAULT_MODEL_FILENAME) as model_file:
        # First creation of example (exit code 0)
        proc = subprocess.run([f"{BIN_NAME}", "example"])
        assert os.path.exists(model_file)
        assert proc.returncode == 0

        # Second creation of example (exit code 1), error because we refuse to overwrite
        proc = subprocess.run([f"{BIN_NAME}", "example"])
        assert proc.returncode == 1

        # We can force write...
        proc = subprocess.run([f"{BIN_NAME}", "example", "-f"])
        assert proc.returncode == 0

    # ----- Different output file name -----
    with clean_run(f'{str(uuid.uuid4())}.json') as model_file:
        proc = subprocess.run([f"{BIN_NAME}", "example", "-o", f"{model_file}"])
        assert proc.returncode == 0


def test_mode_run():
    """
    Test 'run' mode
    """

    with clean_run(DEFAULT_MODEL_FILENAME) as model_file:
        proc = subprocess.run([f"{BIN_NAME}", "example"])
        proc = subprocess.run([f"{BIN_NAME}", "run", f"{model_file}", "--no-plots"])

        proc = subprocess.run([f"{BIN_NAME}", "run", f"{model_file}", "--no-plots", '-v'])
