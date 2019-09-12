#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TEST THE MODEL GENERATOR

    - Serialisation
    - Model import
    - Extension of models
    - Analyses for models made with model generator
"""

import os

import numpy as np
from numpy import cos, sin

import framat.fem.modelgenerator as mg
from framat.stdfun import StdRunArgs, standard_run


TEST_FILENAME = "mg_test_model.json"


os.chdir(os.path.dirname(__file__))


def clean():
    """
    Remove test file if exists
    """

    if os.path.isfile(TEST_FILENAME):
        os.remove(TEST_FILENAME)


def helix(a, b, c, t):
    """
    Make a Helix

    See: https://en.wikipedia.org/wiki/Helix
    """

    x = a*cos(t)
    y = b*sin(t)
    z = c*t
    return (x, y, z)


def test_generate_template():
    """
    Test that model generator creates a template file
    """

    clean()

    modelobj = mg.Model.make_template()
    model = modelobj.serialise(filename=TEST_FILENAME)

    assert os.path.isfile(TEST_FILENAME)

    args = StdRunArgs()
    args._make_plots = False
    standard_run(args=args, model=model)


def test_generate_spiral_beam():
    """
    Create a spiral beam
    """

    modelobj = mg.Model.make_template()
    modelobj.remove_beamlines()

    # Generate node coordinates
    t = np.linspace(0, 20, num=200)
    x, y, z = helix(a=10, b=5, c=0.5, t=t)

    node_list = []
    for x_coord, y_coord, z_coord in zip(x, y, z):
        node_list.append(mg.Node(coord=[x_coord, y_coord, z_coord], up=[0, 0, 1]))

    spiral_beam = mg.BeamLine()
    spiral_beam.append_nodes(node_list)

    # Get UID of first and last node
    node_uids = spiral_beam.get_node_uids()
    first_node_uid = node_uids[0]
    last_node_uid = node_uids[-1]

    # Add material
    spiral_beam.add_const_cross_section(first_node_uid, last_node_uid, "dummy_material", "dummy_profil")

    # Add boundary condition
    bc = mg.BoundaryConditions()
    bc.add_fix(node_uid=first_node_uid)

    modelobj.add_beamline(spiral_beam)
    modelobj.boundary_conditions = bc
    model = modelobj.serialise()

    args = StdRunArgs()
    args._make_plots = False
    standard_run(args=args, model=model)


if __name__ == '__main__':
    test_generate_spiral_beam()
