#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Copyright 2019-2020 Airinnova AB and the FramAT authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------

# Author: Aaron Dettmann

"""
Solving
"""

import itertools
from numbers import Number


def enumerate_with_step(iterable, start=0, step=1):
    """
    TODO
    https://stackoverflow.com/questions/24290025/python-enumerate-downwards-or-with-a-custom-step
    """

    for x in iterable:
        yield (start, x)
        start += step


def pairwise(iterable):
    """
    Return a new iterator which yields pairwise items

    s --> (s0,s1), (s1,s2), (s2, s3), ...

    See: https://docs.python.org/3/library/itertools.html#itertools-recipes
    """

    a, b = itertools.tee(iterable)
    next(b, None)

    return zip(a, b)


class Schemas:
    any_int = {'type': int}
    any_num = {'type': Number}
    pos_int = {'type': int, '>': 0}
    pos_number = {'type': Number, '>': 0}
    string = {'type': str, '>': 0}
    vector3x1 = {'type': list, 'min_len': 3, 'max_len': 3, 'item_types': Number}
    vector6x1 = {'type': list, 'min_len': 6, 'max_len': 6, 'item_types': Number}
