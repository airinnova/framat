#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import numpy as np

import framat.fem.modelgenerator as mg
from framat.stdfun import StdRunArgs, standard_run
from framat.fem.element import Element


@pytest.fixture
def cantilever():
    """
    Cantilever beam
    """

    material = mg.MaterialData(uid="dummy_steel", E=1, G=1, rho=1)
    profil = mg.ProfilData(uid="dummy_profil", A=1, Iy=1, Iz=1, J=1)

    beam1 = mg.BeamLine(uid="beam1", nelem=1)
    beam1.append_nodes(
            [
                mg.Node(uid="node_a", coord=[0, 0, 0], up=[0, 0, 1]),
                mg.Node(uid="node_b", coord=[1, 0, 0], up=[0, 0, 1]),
                mg.Node(uid="node_c", coord=[1, 1, 0], up=[0, 0, 1]),
                ]
            )

    beam1.add_const_cross_section(from_node="node_a", to_node="node_c",
                                  material_uid="dummy_steel", profil_uid="dummy_profil")

    cantilever = mg.Model()
    cantilever.add_beamlines([beam1])
    cantilever.add_material(material)
    cantilever.add_profil(profil)
    cantilever.postproc.add_plot()
    cantilever.acceleration.turn_on = False
    cantilever.boundary_conditions.add_fix(node_uid="node_a", dof=["all"])
    return cantilever


def test_shapefunction_boundaries(cantilever):
    """
    Shape function for left node 1 at left node etc...
    """

    model = cantilever.serialise()

    args = StdRunArgs()
    args.no_plots = False
    results = standard_run(args=args, model=model)
    frame = results['frame']

    element = frame.beamlines[0].elements[0]
    N_0 = element.shape_function_matrix(xi=0)
    N_1 = element.shape_function_matrix(xi=1)

    assert np.testing.assert_array_equal(N_0[0:6, 0:6], np.identity(6)) is None
    assert np.testing.assert_array_equal(N_0[0:6, 6:12], np.zeros((6, 6))) is None
    assert np.testing.assert_array_equal(N_1[0:6, 0:6], np.zeros((6, 6))) is None
    assert np.testing.assert_array_equal(N_1[0:6, 6:12], np.identity(6)) is None

