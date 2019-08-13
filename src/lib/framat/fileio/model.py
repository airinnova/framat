#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Copyright 2019 Airinnova AB and the FramAT authors
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
Model import
"""

import os
import json
import logging

from jsonschema import validate, Draft7Validator
from commonlibs.logger import truncate_filepath

logger = logging.getLogger(__name__)


def load(filename, validate_infile=True):
    """
    Load and validate the model input file in JSON format

    Args:
        :filename: filename (path) of file to import

    Returns:
        :model: raw model data
    """

    logger.info(f"Trying to import file '{truncate_filepath(filename)}'")
    with open(filename, "r") as fp:
        model = json.load(fp)

    # Validate input file with schema
    if validate_infile:
        logger.info(f"Validating input file...")
        my_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(my_path, "model_schema.json")
        with open(path, "r") as fp:
            schema = json.load(fp)

        validate(instance=model, schema=schema, cls=Draft7Validator)

    # Check for duplicate UIDs
    uids = [uid for uid in get_all_values_of_key(model, "uid")]
    duplicate_uids = get_duplicates(uids)

    if duplicate_uids:
        raise ValueError(f"Duplicate UIDs found: {duplicate_uids}")

    return model


def get_duplicates(alist):
    """
    Get duplicate values from a list

    Args:
        :alist: any list

    Returns:
        :duplicates: list with duplicate values
    """

    seen = {}
    duplicates = []

    for entry in alist:
        if entry not in seen:
            seen[entry] = 1
        else:
            if seen[entry] == 1:
                duplicates.append(entry)
            seen[entry] += 1
    return duplicates


def get_all_values_of_key(dictionary, key):
    """
    Yield all values with specified key from a (nested) dictionary

    Args:
        :dictionary: any dictionary

    Yields:
        :values: all values with key
    """

    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in get_all_values_of_key(v, key):
                yield result
        elif isinstance(v, list):
            for d in v:
                if not isinstance(d, (dict, list)):
                    continue
                for result in get_all_values_of_key(d, key):
                    yield result
