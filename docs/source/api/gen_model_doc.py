#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate the model API docuementation
"""

import os

from mframework._documentation import doc2rst

from framat._model import mspec

HERE = os.path.abspath(os.path.dirname(__file__))

file_path = os.path.join(HERE, 'model_api.rst')
doc2rst(mspec.get_docs(), file_path)
