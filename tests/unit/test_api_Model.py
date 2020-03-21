#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test the Python API
"""

import pytest

from framat.model import Model


def test_model_attrs():
    """Test base attributes of the model object"""

    model = Model()
    assert hasattr(model, "material")
    assert hasattr(model, "cross_section")
    assert hasattr(model, "beam")
    assert hasattr(model, "boundary_condition")
    assert hasattr(model, "study")
    assert hasattr(model, "result")


def test_adding_removing():
    """Test basic API adding and removing methods"""

    model = Model()

    # ---------- With explicit UIDs ----------
    model.add_material("steel")
    model.remove_material("steel")
    model.add_beam("cantilever")
    model.remove_beam("cantilever")
    model.add_boundary_condition("fix_root")
    model.remove_boundary_condition("fix_root")
    model.add_study("static")
    model.remove_study("static")
    model.add_result("set1")
    model.remove_result("set1")

    # ---------- Without explicit UIDs ----------
    uid = model.add_material()
    model.remove_material(uid)
    uid = model.add_beam()
    model.remove_beam(uid)
    uid = model.add_boundary_condition()
    model.remove_boundary_condition(uid)
    uid = model.add_study()
    model.remove_study(uid)
    uid = model.add_result()
    model.remove_result(uid)


def test_basic_modelling():
    """Test that modelling API doesn"t throw unexpected errors"""

    model = Model()

    model.add_material("steel")
    model.material["steel"].set("E", 2.1e9)
    model.material["steel"].set("G", 0.81e9)
    model.material["steel"].set("rho", 7800)
    with pytest.raises(KeyError):
        model.material["steel"].set("PROPERTY_DOES_NOT_EXIST", 1)

    model.add_cross_section("cs")
    model.cross_section["cs"].set("A", 0.1)
    model.cross_section["cs"].set("Iy", 1)
    model.cross_section["cs"].set("Iz", 1)
    model.cross_section["cs"].set("J", 1)
    with pytest.raises(KeyError):
        model.cross_section["steel"].set("PROPERTY_DOES_NOT_EXIST", 1)

    model.add_beam("cantilever")
    model.beam["cantilever"].set("nelem", 100)
    model.beam["cantilever"].add("node", {"uid": "root", "coord": [0, 0, 0]})
    model.beam["cantilever"].add("node", {"uid": "tip", "coord": [1, 0, 0]})
    model.beam["cantilever"].add("material", {"from": "root", "to": "tip", "uid": "steel"})
    model.beam["cantilever"].add("cross_section", {"from": "root", "to": "tip", "uid": "cs"})
    model.beam["cantilever"].add("orientation", {"from": "root", "to": "tip", "up": [0, 0, 1]})
    model.beam["cantilever"].add("load", {"at": "tip", "load": [0, 0, 1, 0, 0, 0]})

    model.add_boundary_condition("bc")
    model.boundary_condition["bc"].add("fix", {"node": "root", "fix": ["all"]})

    model.add_study("s1")
    model.study["s1"].set("type", "stationary")

    model.add_result("r1")
    # model.result["r1"].add()
