#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import numpy as np

import framat.fem.modelgenerator as mg
from framat.stdfun import StdRunArgs, standard_run


def test_cantilever_point_load():
    """
    Cantilever beam with a point load Pz at its tip
    """

    Pz = 1  # Tip point load
    E = 1  # Young's modulus
    Iy = 1  # 2nd moment of area about y-axis

    ### Iz should not change any results...
    Iz = 2  # 2nd moment of area about z-axis

    L = 1  # Beam length

    def deflection_uz_analytical(x):
        """
        Analytical expression for the deflection curve

        Args:
            :x: x position
        """
        # Iy = 1

        ux = 0
        uy = 0
        uz = (Pz/(6*E*Iy))*(3*L*x**2 - x**3)
        tx = 0
        ty = -(Pz/(6*E*Iy))*(6*L*x - 3*x**2)
        tz = 0

        return [ux, uy, uz, tx, ty, tz]

    modelobj = mg.Model.make_template()
    modelobj.profildata['dummy_profil'].Iz = Iz
    modelobj.profildata['dummy_profil'].Iy = Iy
    beamline_uid = modelobj.get_beamline_uids(beam_number=0)
    modelobj.beamlines[beamline_uid].add_concentrated_load(node_uid="node_b", load=[0, 0, Pz, 0, 0, 0])
    modelobj.beamlines[beamline_uid].nelem = 10
    model = modelobj.serialise()

    args = StdRunArgs()
    args._make_plots = False
    results = standard_run(args=args, model=model)
    frame = results['frame']
    def_interpolator = frame.deformation.get_beamline_interpolator('cantilever', frame)

    # Test deformation at different positions along the beam line
    for x in np.linspace(0, 1, 20):
        def_FEM = def_interpolator(x)
        def_ANALYTICAL = deflection_uz_analytical(x)
        assert def_FEM == pytest.approx(def_ANALYTICAL)


# def test_cantilever_distributed_load():
#     """
#     Cantilever beam with a distributed moment
#     """

#     my0 = 1

#     E = 1  # Young's modulus
#     Iy = 1  # 2nd moment of area about y-axis
#     L = 1

#     def deflection_uz_analytical(x):
#         """
#         Analytical expression for the deflection curve

#         Args:
#             :x: x position
#         """
#         # Iy = 1

#         ux = 0
#         uy = 0
#         uz = (my0/(E*Iy))*((L*x**2)/2 - (x**3)/6)
#         tx = 0
#         ty = -(my0/(E*Iy))*(L*x - (x**2)/2)
#         tz = 0

#         return [ux, uy, uz, tx, ty, tz]

#     modelobj = mg.Model.make_template()
#     # modelobj.profildata['dummy_profil'].Iz = Iz
#     modelobj.profildata['dummy_profil'].Iy = Iy
#     modelobj.beamlines['cantilever'].add_const_distributed_load(from_node_uid="node_a", to_node_uid="node_b", load=[0, 0, 0, 0, 1, 0])
#     modelobj.beamlines['cantilever'].nelem = 10
#     model = modelobj.serialise("m-test.json")

#     args = StdRunArgs()
#     args._make_plots = False
#     results = standard_run(args=args, model=model)
#     frame = results['frame']
#     def_interpolator = frame.deformation.get_beamline_interpolator('cantilever', frame)

#     # Test deformation at different positions along the beam line
#     for x in np.linspace(0, 1, 20):
#         def_FEM = def_interpolator(x)
#         def_ANALYTICAL = deflection_uz_analytical(x)
#         print()
#         print(def_FEM)
#         print(def_ANALYTICAL)
#         assert def_FEM == pytest.approx(def_ANALYTICAL)
