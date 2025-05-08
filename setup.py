#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import setuptools
import os

# See also: https://github.com/kennethreitz/setup.py/blob/master/setup.py

NAME = 'framat'
VERSION = '0.3'
AUTHOR = 'Aaron Dettmann'
EMAIL = 'dettmann@kth.se'
DESCRIPTION = 'FramAT (Frame Analysis Tool) is a tool for 3D FEM beam analyses'
URL = 'https://github.com/airinnova/framat'
REQUIRES_PYTHON = '>=3.6.0'
REQUIRED = [
    'commonlibs>=0.3.3',
    'jsonschema',
    'matplotlib>=3.4.0',
    'numpy',
    'scipy',
    'model-framework>=0.0.14',
]
PACKAGE_DIR = 'src'
LICENSE = 'Apache License 2.0'
SCRIPTS = []

setuptools.setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description=open("README.md").read(),
    long_description_content_type = "text/markdown",
    url=URL,
    include_package_data=True,
    scripts=SCRIPTS,
    package_dir={'': PACKAGE_DIR},
    license=LICENSE,
    # packages=[NAME],
    packages=setuptools.find_packages(where=PACKAGE_DIR),
    python_requires=REQUIRES_PYTHON,
    install_requires=REQUIRED,
    # See: https://pypi.org/classifiers/
    classifiers=[
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.11',
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)
