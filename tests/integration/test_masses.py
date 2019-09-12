#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Comparison with COMSOL Multiphysics version 5.4

https://www.comsol.se/
"""


import pytest

import framat.fem.modelgenerator as mg
from framat.stdfun import StdRunArgs, standard_run

BEAM_A = 1
BEAM_LEN = 2
BEAM_RHO = 1
BEAM_MASS = BEAM_A*BEAM_LEN*BEAM_RHO


@pytest.fixture
def cantilever():
    """
    Cantilever beam
    """

    material = mg.MaterialData(uid="dummy_steel", E=1, G=1, rho=BEAM_RHO)
    profil = mg.ProfilData(uid="dummy_profil", A=BEAM_A, Iy=1, Iz=1, J=1)

    beam1 = mg.BeamLine(uid="beam1", nelem=14)
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
    cantilever.postproc.save_results["mass_breakdown"] = True
    cantilever.boundary_conditions.add_fix(node_uid="node_a", dof=["all"])
    return cantilever


def test_structure_mass(cantilever):
    model = cantilever.serialise()

    args = StdRunArgs()
    args._make_plots = False
    results = standard_run(args=args, model=model)
    frame = results['frame']

    mb = frame.mass_breakdown
    assert mb['total_mass'] == BEAM_MASS


def test_structure_additional_masses(cantilever):
    point_mass_a = 30
    point_mass_b = 10
    point_mass_c = 20
    cantilever.beamlines['beam1'].add_point_mass(node_uid='node_a', mass=point_mass_a)
    cantilever.beamlines['beam1'].add_point_mass(node_uid='node_b', mass=point_mass_b)
    cantilever.beamlines['beam1'].add_point_mass(node_uid='node_c', mass=point_mass_c)
    model = cantilever.serialise()

    args = StdRunArgs()
    args._make_plots = False
    results = standard_run(args=args, model=model)
    frame = results['frame']

    mb = frame.mass_breakdown
    assert mb['total_mass'] == pytest.approx(BEAM_MASS + point_mass_a + point_mass_b + point_mass_c)
