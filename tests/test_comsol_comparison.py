#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Comparison with COMSOL Multiphysics version 5.4

https://www.comsol.se/
"""


import pytest

import framat.fem.modelgenerator as mg
from framat.stdfun import StdRunArgs, standard_run


def round2zero(array, limit=1e-9):
    """
    Make small numbers zero
    """

    new_array = []
    for num in array:
        if abs(num) <= limit:
            num = 0
        new_array.append(num)

    return new_array


@pytest.fixture
def cantilever():
    """
    Cantilever beam
    """

    material = mg.MaterialData(uid="dummy_steel", E=1, G=1, rho=1)
    profil = mg.ProfilData(uid="dummy_profil", A=1, Iy=1, Iz=1, J=1)

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
    cantilever.boundary_conditions.add_fix(node_uid="node_a", dof=["all"])
    return cantilever


def test_cantilever_pointload1(cantilever):
    """
    COMSOL
    """

    cantilever.beamlines['beam1'].add_concentrated_load(node_uid="node_b", load=[0, 0, 1, 0, 0, 0])
    model = cantilever.serialise()

    args = StdRunArgs()
    args._make_plots = False
    results = standard_run(args=args, model=model)
    frame = results['frame']

    comsol = {}
    comsol['node_b'] = [0.000000000000000E0, 0.000000000000000E0, 3.333333333339483E-1, 2.986429541369149E-13, -5.000000000004997E-1, 0.000000000000000E0]
    comsol['node_c'] = [0.000000000000000E0, 0.000000000000000E0, 3.333333333339483E-1, 2.986429541369149E-13, -5.000000000004997E-1, 0.000000000000000E0]

    for node_uid in ['node_b', 'node_c']:
        tip_node_number = frame.finder.nodes.by_uid[node_uid].num
        u_framat = frame.deformation.by_node_num(tip_node_number)
        u_comsol = comsol[node_uid]
        u_framat = round2zero(u_framat)
        u_comsol = round2zero(u_comsol)
        assert u_framat == pytest.approx(u_comsol)


def test_cantilever_pointload2(cantilever):
    """
    COMSOL
    """

    cantilever.beamlines['beam1'].add_concentrated_load(node_uid="node_b", load=[0, 0, 1, 1, 1, 1])
    model = cantilever.serialise()

    args = StdRunArgs()
    args._make_plots = False
    results = standard_run(args=args, model=model)
    frame = results['frame']

    comsol = {}
    comsol['node_b'] = [-8.651084788930832E-13, 5.000000000006578E-1, -1.666666666665981E-1, 1.000000000000388E0, 4.999999999998941E-1, 1.000000000001180E0]
    comsol['node_c'] = [-1.000000000002333E0, 5.000000000006555E-1, 8.333333333339423E-1, 1.000000000000613E0, 4.999999999998925E-1, 1.000000000001609E0]

    for node_uid in ['node_b', 'node_c']:
        tip_node_number = frame.finder.nodes.by_uid[node_uid].num
        u_framat = frame.deformation.by_node_num(tip_node_number)
        u_comsol = comsol[node_uid]
        u_framat = round2zero(u_framat)
        u_comsol = round2zero(u_comsol)
        assert u_framat == pytest.approx(u_comsol)


def test_cantilever_pointload3(cantilever):
    """
    COMSOL
    """

    cantilever.beamlines['beam1'].add_concentrated_load(node_uid="node_c", load=[1, 1, 1, 1, 1, 1])
    model = cantilever.serialise()

    args = StdRunArgs()
    args._make_plots = False
    results = standard_run(args=args, model=model)
    frame = results['frame']

    comsol = {}
    comsol['node_b'] = [1.000000000000718E0, 3.333333333333479E-1, -1.666666666662542E-1, 2.000000000001323E0, 4.999999999993773E-1, 4.999999999999319E-1]
    comsol['node_c'] = [3.333333333341866E-1, 1.333333333333342E0, 2.666666666668882E0, 3.500000000002027E0, 1.499999999999372E0, 9.999999999998267E-1]

    for node_uid in ['node_b', 'node_c']:
        tip_node_number = frame.finder.nodes.by_uid[node_uid].num
        u_framat = frame.deformation.by_node_num(tip_node_number)
        u_comsol = comsol[node_uid]
        u_framat = round2zero(u_framat)
        u_comsol = round2zero(u_comsol)
        assert u_framat == pytest.approx(u_comsol)


def test_cantilever_dist_load1(cantilever):
    """
    COMSOL
    """

    cantilever.beamlines['beam1'].add_const_distributed_load(from_node_uid="node_a", to_node_uid="node_b", load=[1, 1, 1, 0, 0, 0])
    model = cantilever.serialise()

    args = StdRunArgs()
    args._make_plots = False
    results = standard_run(args=args, model=model)
    frame = results['frame']

    comsol = {}
    comsol['node_b'] = [5.000000000004979E-1, 1.249999999998921E-1, 1.250000000001275E-1, 8.641212599618681E-14, -1.666666666668539E-1, 1.666666666664287E-1]
    comsol['node_c'] = [3.333333333341506E-1, 1.249999999998916E-1, 1.250000000002308E-1, 1.119263615314014E-13, -1.666666666668533E-1, 1.666666666663053E-1]

    for node_uid in ['node_b', 'node_c']:
        tip_node_number = frame.finder.nodes.by_uid[node_uid].num
        u_framat = frame.deformation.by_node_num(tip_node_number)
        u_comsol = comsol[node_uid]
        u_framat = round2zero(u_framat)
        u_comsol = round2zero(u_comsol)
        print()
        print(u_framat)
        print(u_comsol)
        assert u_framat == pytest.approx(u_comsol)


def test_cantilever_dist_load2(cantilever):
    """
    COMSOL
    """

    cantilever.beamlines['beam1'].add_const_distributed_load(from_node_uid="node_a", to_node_uid="node_b", load=[0, 0, 0, 1, 0, 0])
    model = cantilever.serialise()

    args = StdRunArgs()
    args._make_plots = False
    results = standard_run(args=args, model=model)
    frame = results['frame']

    comsol = {}
    comsol['node_b'] = [0.000000000000000E0, 0.000000000000000E0, 1.151905288530186E-13, 5.000000000002529E-1, -1.727661140969786E-13, 0.000000000000000E0]
    comsol['node_c'] = [0.000000000000000E0, 0.000000000000000E0, 5.000000000004560E-1, 5.000000000003826E-1, -1.727501420150245E-13, 0.000000000000000E0]

    for node_uid in ['node_b', 'node_c']:
        tip_node_number = frame.finder.nodes.by_uid[node_uid].num
        u_framat = frame.deformation.by_node_num(tip_node_number)
        u_comsol = comsol[node_uid]
        u_framat = round2zero(u_framat)
        u_comsol = round2zero(u_comsol)
        assert u_framat == pytest.approx(u_comsol)


def test_cantilever_dist_load3(cantilever):
    """
    COMSOL
    """

    cantilever.beamlines['beam1'].add_const_distributed_load(from_node_uid="node_a", to_node_uid="node_b", load=[0, 0, 0, 0, 1, 1])
    model = cantilever.serialise()

    args = StdRunArgs()
    args._make_plots = False
    results = standard_run(args=args, model=model)
    frame = results['frame']

    comsol = {}
    comsol['node_b'] = [-4.325195747555271E-13, 3.333333333336428E-1, -3.333333333336693E-1, -2.303925454661278E-13, 5.000000000004943E-1, 5.000000000005623E-1]
    comsol['node_c'] = [-5.000000000011393E-1, 3.333333333336411E-1, -3.333333333339448E-1, -2.978775793467516E-13, 5.000000000004926E-1, 5.000000000007775E-1]

    for node_uid in ['node_b', 'node_c']:
        tip_node_number = frame.finder.nodes.by_uid[node_uid].num
        u_framat = frame.deformation.by_node_num(tip_node_number)
        u_comsol = comsol[node_uid]
        u_framat = round2zero(u_framat)
        u_comsol = round2zero(u_comsol)
        assert u_framat == pytest.approx(u_comsol)

##############################################################################
##############################################################################
# TEST CASE 2 (2-beam-structure)
##############################################################################
##############################################################################

@pytest.fixture
def modelobj():
    """
    Structure with two beams
    """

    E = 210e9
    G = 81e9
    rho = 7850
    A = 0.01
    Iy = 8.333e-6
    Iz = 8.333e-6
    J = 2.25e-4

    material = mg.MaterialData(uid="dummy_steel", E=E, G=G, rho=rho)
    profil = mg.ProfilData(uid="dummy_profil", A=A, Iy=Iy, Iz=Iz, J=J)

    beam1 = mg.BeamLine(uid="beam1", nelem=12)
    beam1.append_nodes(
            [
                mg.Node(uid="node_a", coord=[0, -5, 0], up=[-1, 0, 0]),
                mg.Node(uid="node_b", coord=[0, -5, 5], up=[0, 0, 1]),
                mg.Node(uid="node_c", coord=[5, -5, 5], up=[0, 0, 1]),
                mg.Node(uid="node_d", coord=[5, 0, 5], up=[0, 0, 1]),
                ]
            )

    beam1.add_const_cross_section(from_node="node_a", to_node="node_d",
                                  material_uid="dummy_steel", profil_uid="dummy_profil")

    beam2 = mg.BeamLine(uid="beam2", nelem=6)
    beam2.append_nodes(
            [
                mg.Node(uid="node_e", coord=[0, 0, 8], up=[0, 0, 1]),
                mg.Node(uid="node_f", coord=[5, -5, 8], up=[0, 0, 1]),
                ]
            )

    beam2.add_const_cross_section(from_node="node_e", to_node="node_f",
                                  material_uid="dummy_steel", profil_uid="dummy_profil")

    modelobj = mg.Model()
    modelobj.add_beamlines([beam1, beam2])
    modelobj.add_material(material)
    modelobj.add_profil(profil)
    modelobj.postproc.add_plot()
    modelobj.acceleration.turn_on = False
    modelobj.boundary_conditions.add_fix(node_uid="node_a", dof=["all"])
    modelobj.boundary_conditions.add_fix(node_uid="node_e", dof=["ux", "uy", "uz"])
    modelobj.boundary_conditions.add_connection(node1_uid="node_c", node2_uid="node_f", dof=["all"])
    return modelobj


def test_point_load1(modelobj):
    """
    COMSOL
    """

    modelobj.beamlines['beam1'].add_concentrated_load(node_uid="node_c", load=[0, 0, -1000, 0, 0, 0])
    model = modelobj.serialise()

    args = StdRunArgs()
    args._make_plots = False
    results = standard_run(args=args, model=model)
    frame = results['frame']

    comsol = {}
    comsol['node_b'] = [1.066891478253068E-2, 9.543646272022848E-3, -1.983119895890568E-6, -3.001070495297579E-3, 5.585818521450960E-3, 7.594567199847793E-4]
    comsol['node_c'] = [1.066759658265234E-2, 2.903277892984416E-2, -4.186652047476606E-2, -3.054063508322713E-3, 9.176797196636636E-3, 6.219808329632239E-3]
    comsol['node_d'] = [-2.043144506550915E-2, 2.903277892984415E-2, -5.713683801638100E-2, -3.054063508323112E-3, 9.176797196636654E-3, 6.219808329632350E-3]
    comsol['node_f'] = [3.819798817231467E-2, 3.819496945534988E-2, -4.186652047446178E-2, -3.054063508318770E-3, 9.176797196697322E-3, 6.219808329766303E-3]

    for node_uid in ['node_b', 'node_c', 'node_d', 'node_f']:
        tip_node_number = frame.finder.nodes.by_uid[node_uid].num
        u_framat = frame.deformation.by_node_num(tip_node_number)
        u_comsol = comsol[node_uid]
        assert u_framat == pytest.approx(u_comsol)


def test_point_load2(modelobj):
    """
    COMSOL
    """

    modelobj.beamlines['beam1'].add_concentrated_load(node_uid="node_c", load=[0, 0, -1000, -200, -200, -200])
    model = modelobj.serialise()

    args = StdRunArgs()
    args._make_plots = False
    results = standard_run(args=args, model=model)
    frame = results['frame']

    comsol = {}
    comsol['node_b'] = [1.002048959214114E-2, 9.123474179897293E-3, -1.964573487084554E-6, -2.915664469260097E-3, 5.285385109330331E-3, 6.809300927723490E-4]
    comsol['node_c'] = [1.001921245395625E-2, 2.658870914265197E-2, -3.939801207117682E-2, -2.984268337178663E-3, 8.508381816577183E-3, 5.571438689630761E-3]
    comsol['node_d'] = [-1.783798099419770E-2, 2.658870914265195E-2, -5.431935375707141E-2, -2.984268337179038E-3, 8.508381816577190E-3, 5.571438689630833E-3]
    comsol['node_f'] = [3.554435790346207E-2, 3.554151415469307E-2, -3.939801207089391E-2, -2.984268337174976E-3, 8.508381816633659E-3, 5.571438689755973E-3]

    for node_uid in ['node_b', 'node_c', 'node_d', 'node_f']:
        tip_node_number = frame.finder.nodes.by_uid[node_uid].num
        u_framat = frame.deformation.by_node_num(tip_node_number)
        u_comsol = comsol[node_uid]
        assert u_framat == pytest.approx(u_comsol)


def test_dist_load1(modelobj):
    """
    COMSOL
    """

    modelobj.beamlines['beam1'].add_const_distributed_load(from_node_uid="node_b", to_node_uid="node_c", load=[1000, 1000, 1000, 0, 0, 0])
    model = modelobj.serialise()

    args = StdRunArgs()
    args._make_plots = False
    results = standard_run(args=args, model=model)
    frame = results['frame']

    comsol = {}
    comsol['node_b'] = [6.732757111460135E-2, 3.652905973076431E-2, 1.247202082849881E-5, -6.601864577506486E-3, 1.304871265636743E-2, 2.290343746451240E-3]
    comsol['node_c'] = [6.733550049414583E-2, 8.244665025538872E-2, -4.121655548443893E-2, -4.928517336182789E-3, 9.962799017880077E-3, 1.401955220574270E-2]
    comsol['node_d'] = [-2.762260534566513E-3, 8.244665025538851E-2, -6.585914216535620E-2, -4.928517336183659E-3, 9.962799017880062E-3, 1.401955220574240E-2]
    comsol['node_f'] = [9.722389754805007E-2, 9.723220226485939E-2, -4.121655548428723E-2, -4.928517335832289E-3, 9.962799017873893E-3, 1.401955220604765E-2]

    for node_uid in ['node_b', 'node_c', 'node_d', 'node_f']:
        tip_node_number = frame.finder.nodes.by_uid[node_uid].num
        u_framat = frame.deformation.by_node_num(tip_node_number)
        u_comsol = comsol[node_uid]
        assert u_framat == pytest.approx(u_comsol)

# def test_dist_load2(modelobj):
#     """
#     COMSOL
#     """

#     modelobj.beamlines['beam1'].add_const_distributed_load(from_node_uid="node_c", to_node_uid="node_d", load=[1000,1000,1000,0,0,0])
#     model = modelobj.serialise()

#     args = StdRunArgs()
#     args._make_plots = False
#     results = standard_run(args=args, model=model)
#     frame = results['frame']

#     comsol = {}
#     comsol['node_b'] = [2.169031463327843E-2, -1.374872934737870E-2, 1.017598786418729E-5, 1.374975761389203E-2, -7.503665166533954E-3, 9.667484118134897E-4]
#     comsol['node_c'] = [2.170649377710662E-2, -2.499532438718028E-2, 1.267541227857880E-1, 1.744650804620378E-2, -3.301751863265106E-2, -1.371565230267489E-2]
#     comsol['node_d'] = [1.349293982190591E-1, -2.498937200622789E-2, 2.586313059453878E-1, 2.935174616049219E-2, -3.301751863265110E-2, -2.562089041696247E-2]
#     # comsol['node_f'] = [1.349293982190591E-1, -2.498937200622789E-2, 2.586313059453878E-1, 2.935174616049219E-2, -3.301751863265110E-2, -2.562089041696247E-2]                    ##  COPIED WRONG ???

#     for node_uid in ['node_b', 'node_c', 'node_d', 'node_f']:
#         tip_node_number = frame.finder.nodes.by_uid[node_uid].num
#         u_framat = frame.deformation.by_node_num(tip_node_number)
#         u_comsol = comsol[node_uid]
#         print(node_uid)
#         print(u_framat)
#         print(u_comsol)
#         assert u_framat == pytest.approx(u_comsol)


def test_gravity_load1(modelobj):
    """
    COMSOL
    """

    modelobj.acceleration.direction = [0, 0, -50]
    modelobj.acceleration.turn_on = True
    model = modelobj.serialise()

    args = StdRunArgs()
    args._make_plots = False
    results = standard_run(args=args, model=model)
    frame = results['frame']

    comsol = {}
    comsol['node_b'] = [5.596076482184879E-1, 4.762117782171238E-1, -1.321409332803191E-4, -1.698801746334137E-1, 2.758114598130918E-1, 2.993944464887873E-2]
    comsol['node_c'] = [5.595556818966981E-1, 1.302412325985819E0, -1.972980221323205E0, -1.802565216028734E-1, 4.279096128123204E-1, 2.799362378051662E-1]
    comsol['node_d'] = [-8.401255071291417E-1, 1.302412325985816E0, -3.049493052832375E0, -2.269845812014872E-1, 4.279096128123197E-1, 2.799362378051689E-1]
    comsol['node_f'] = [1.843284520339020E0, 1.843181890812329E0, -1.972980221320200E0, -1.802565215961649E-1, 4.279096128122850E-1, 2.799362378154024E-1]

    for node_uid in ['node_b', 'node_c', 'node_d', 'node_f']:
        tip_node_number = frame.finder.nodes.by_uid[node_uid].num
        u_framat = frame.deformation.by_node_num(tip_node_number)
        u_comsol = comsol[node_uid]
        assert u_framat == pytest.approx(u_comsol)
