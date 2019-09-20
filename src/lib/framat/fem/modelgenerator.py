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
Frame model generator
"""

import uuid
import json
from collections import OrderedDict, defaultdict

from framat.fem.plot import PLOT3D_DEFAULTS

STD_GRAV_ACCEL = 9.81


def get_uuid():
    """
    Return a (universally) unique identifier in a string representation

    Note:
        * This function uses UUID4,
          see https://en.wikipedia.org/wiki/Universally_unique_identifier
    """

    return str(uuid.uuid4())


class Model:

    def __init__(self):
        """
        Top-level model object

        This object includes the entire model defintion and can be serialised
        """

        self.beamlines = OrderedDict()

        self.materialdata = {}
        self.profildata = {}

        self.acceleration = Acceleration()
        self.boundary_conditions = BoundaryConditions()

        self.analysis = {
            "static": True,
            "free_vibrations": False,
        }

        self.postproc = PostProc()

    @classmethod
    def make_template(cls):
        """
        Return a minimal working example of a model definition

        Note:
            * A simple cantilever beam will be return, with a tip and a root node
            * The root node is clamped

        Returns:
            :modelobj: model definition object
        """

        modelobj = cls()

        # Add a beamline
        beamline = BeamLine.make_cantilever(uid="cantilever")
        modelobj.add_beamline(beamline)

        # Add a material and profil database entry
        modelobj.add_material(MaterialData(uid="dummy_material"))
        modelobj.add_profil(ProfilData(uid="dummy_profil"))

        # Add the acceleration and boundary conditions
        modelobj.update_acceleration(Acceleration(turn_on=False))
        modelobj.boundary_conditions = BoundaryConditions()
        modelobj.boundary_conditions.add_fix("node_a")

        # Add post processing fields
        postproc = PostProc()
        postproc.add_plot()
        modelobj.postproc = postproc

        return modelobj

    @classmethod
    def import_from_dict(cls, modeldict):
        """
        Convert a dictionary into a model object

        Args:
            :modeldict: dictionary of the model definition

        Returns:
            :TODO:
        """

        raise NotImplementedError

    def add_beamlines(self, beamlines):
        for beamline in beamlines:
            self.add_beamline(beamline)

    def add_beamline(self, beamline):
        self.beamlines[beamline.uid] = beamline

    def remove_beamline(self, beamline_uid):
        raise NotImplementedError

    def remove_beamlines(self):
        """
        Remove all beamlines and boundary conditions
        """

        self.beamlines = {}
        self.boundary_conditions = {}

    def get_beamline_uids(self, beam_number=None):
        beamline_uids = list(self.beamlines.keys())

        if beam_number is not None:
            return str(beamline_uids[beam_number])
        else:
            return beamline_uids

    def add_material(self, material):
        self.materialdata[material.uid] = material

    def remove_material(self, material_uid):
        raise NotImplementedError

    def add_profil(self, profil):
        self.profildata[profil.uid] = profil

    def remove_profil(self, profil_uid):
        raise NotImplementedError

    def update_acceleration(self, acceleration):
        self.acceleration = acceleration

    def serialise(self, filename=None):
        """
        Return a dictionary object and write to a JSON file (optional)

        Args:
            :filename: if provided a

        Returns:
            :modeldict: model definition object converted into a dictionary
        """

        modeldict = {}

        # ===== Beamlines =====
        modeldict['beamlines'] = []
        for beamline in self.beamlines.values():
            beamline_entry = {}
            beamline_entry['uid'] = beamline.uid
            beamline_entry['nelem'] = beamline.nelem
            beamline_entry['beamprops'] = beamline.beamprops
            beamline_entry['loads'] = beamline.loads
            beamline_entry['free_node_mapping'] = beamline.free_node_mapping

            beamline_entry['nodes'] = []
            for node in beamline.nodes.values():
                node_entry = {}
                node_entry['uid'] = node.uid
                node_entry['coord'] = node.coord
                node_entry['up'] = node.up
                beamline_entry['nodes'].append(node_entry)

            modeldict['beamlines'].append(beamline_entry)

        # ===== Material database =====
        modeldict['materialdata'] = []
        for material in self.materialdata.values():
            material_entry = {}
            material_entry['uid'] = material.uid
            material_entry['E'] = material.E
            material_entry['G'] = material.G
            material_entry['rho'] = material.rho

            modeldict['materialdata'].append(material_entry)

        # ===== Profil database =====
        modeldict['profildata'] = []
        for profil in self.profildata.values():
            profil_entry = {}
            profil_entry['uid'] = profil.uid
            profil_entry['A'] = profil.A
            profil_entry['Iy'] = profil.Iy
            profil_entry['Iz'] = profil.Iz
            profil_entry['J'] = profil.J

            modeldict['profildata'].append(profil_entry)

        # ===== Acceleration =====
        modeldict['acceleration'] = {}
        modeldict['acceleration']['turn_on'] = self.acceleration.turn_on
        modeldict['acceleration']['direction'] = self.acceleration.direction
        modeldict['acceleration']['accel_factor'] = self.acceleration.accel_factor

        # ===== Boundary conditions =====
        modeldict['boundary_conditions'] = defaultdict(list)

        for fix in self.boundary_conditions.fix:
            modeldict['boundary_conditions']["fix"].append(fix)

        for connection in self.boundary_conditions.connect:
            modeldict['boundary_conditions']["connect"].append(connection)

        # ===== Analysis =====
        modeldict['analysis'] = self.analysis

        # ===== Post processing =====
        modeldict['postproc'] = {}
        modeldict['postproc']['plots'] = self.postproc.plots
        modeldict['postproc']['save_results'] = self.postproc.save_results

        if filename:
            with open(filename, "w") as fp:
                json.dump(modeldict, fp, indent=4)

        return modeldict


class BeamLine:

    def __init__(self, uid=None, nelem=1):
        """
        Beamline definition object

        Args:
            :uid: UID of the beamline
            :nelem: number of elements of the beamline
        """

        if uid is None:
            uid = get_uuid()

        self.uid = uid
        self.nelem = nelem

        self.free_node_mapping = None

        self.nodes = OrderedDict()  # nodes must be ordered!
        self.beamprops = []
        self.loads = {}
        self.reset_loads()

    @classmethod
    def make_cantilever(cls, uid=None):
        """
        Return a basic cantilever beamline
        """

        node1 = Node(uid="node_a", coord=[0, 0, 0], up=[0, 0, 1])
        node2 = Node(uid="node_b", coord=[1, 0, 0], up=[0, 0, 1])

        beamline = cls(uid=uid)
        beamline.append_nodes([node1, node2])

        beamline.beamprops.append({
            "from": node1.uid,
            "to": node2. uid,
            "constant": {
                "material": "dummy_material",
                "profil": "dummy_profil"
                },
            })

        return beamline

    def append_nodes(self, nodes):
        for node in nodes:
            self.append_node(node)

    def append_node(self, node):
        if node.uid in self.uid:
            raise RuntimeError

        self.nodes[node.uid] = node

    def get_node_uids(self, node_num=None):
        node_uids = list(self.nodes.keys())

        if node_num is not None:
            return node_uids[node_num]
        else:
            return node_uids

    def delete_node(self, node_uid):
        raise NotImplementedError

    def add_const_cross_section(self, from_node, to_node, material_uid, profil_uid):
        self.beamprops.append({
            "from": from_node,
            "to": to_node,
            "constant": {
                "material": material_uid,
                "profil": profil_uid
                }
            })

    def add_point_mass(self, node_uid, mass):
        self.beamprops.append({
            "at": node_uid,
            "pointmass": mass,
            })

    def move(self, direction, steps=1):
        """
        Shift all nodes of the beamline

        Args:
            :direction: vector with direction along which nodes are to be shifted
            :steps: nodes are shifted :steps: times :direction:
        """

        raise NotImplementedError

    def rotate(self, rot_axis, degree):
        """
        Rotate all nodes of the beamline

        Args:
            :rot_axis: rotation axis around which nodes are to be rotated
            :degree: degrees by which to rotate
        """

        raise NotImplementedError

    def reset_loads(self):
        self.loads = {}
        self.loads['concentrated'] = []
        self.loads['distributed'] = []
        self.loads['free_nodes'] = []

    def add_concentrated_load(self, node_uid, load):
        self.loads['concentrated'].append({
            "node": node_uid,
            "load": load,
            })

    def add_free_node_load(self, coord, load):
        self.loads['free_nodes'].append({
            "coord": coord,
            "load": load,
            })

    def add_const_distributed_load(self, from_node_uid, to_node_uid, load):
        self.loads['distributed'].append({
            "from": from_node_uid,
            "to": to_node_uid,
            "constant": load,
            })


class Node:

    def __init__(self, uid=None, coord=None, up=None):
        """
        Node definition

        Args:
            :uid: UID of the node
            :coord: coordinate of the node
            :up: up direction
        """

        if uid is None:
            uid = get_uuid()

        self.uid = uid
        self.coord = coord
        self.up = up


class FreeNodeLoad:

    def __init__(self, coord, load, dest_node=None):
        """
        Free node load definition

        Args:
            :coord: coordinate of the free node load
            :load: concentrated load as a vector
            :dest_node: destination load
        """

        raise NotImplementedError


class MaterialData:

    def __init__(self, uid=None, E=1, G=1, rho=1):
        """
        Material data definition

        Args:
            :uid: UID of the material
            :E: ...
            :G: ...
            :rho: ...
        """

        if uid is None:
            uid = get_uuid()

        self.uid = uid
        self.E = E
        self.G = G
        self.rho = rho


class ProfilData:

    def __init__(self, uid=None, A=1, Iy=1, Iz=1, J=1):
        """
        Profil data definition

        Args:
            :uid: UID of the profil
            :A: ...
            :Iy: ...
            :Iz: ...
            :J: ...
        """

        if uid is None:
            uid = get_uuid()

        self.uid = uid
        self.A = A
        self.Iy = Iy
        self.Iz = Iz
        self.J = J


class Acceleration:

    def __init__(self, turn_on=False, direction=[0, 0, -STD_GRAV_ACCEL], accel_factor=1):
        """
        Acceleration definition

        Args:
            :turn_on: flag indicating whether to accelerate the frame or not
            :direction: direction of the acceleration
            :accel_factor: 'load factor'
        """

        self.turn_on = turn_on
        self.direction = direction
        self.accel_factor = accel_factor


class BoundaryConditions:

    def __init__(self):
        """
        Definition of the boundary conditions
        """

        self.fix = []
        self.connect = []

    def add_fix(self, node_uid, dof=["all"]):
        fix_entry = {"node": node_uid, "fix": dof}
        self.fix.append(fix_entry)

    def remove_fix(self, node_uid):
        raise NotImplementedError

    def add_connection(self, node1_uid, node2_uid, dof=["all"]):
        connect_entry = {"node1": node1_uid, "node2": node2_uid, "fix": dof}
        self.connect.append(connect_entry)

    def remove_connection(self, node_uid):
        raise NotImplementedError


class PostProc:

    def __init__(self):
        """
        Definition of the post-processing """

        self.plots = []
        self.save_results = {
            "nodal_deformation": False,
            "mass_breakdown": False,
            "work_breakdown": False,
        }

    def add_plot(self):
        plot_entry = {}

        for default in PLOT3D_DEFAULTS:
            setting, value = default
            plot_entry[setting] = value

        self.plots.append(plot_entry)

    def clear_plots(self):
        self.plots = []


def get_example(model_name='cantilever'):
    """
    Return an example model object

    Args:
        :model_name: TODO

    Returns:
        :modelobj: Model object instance
    """

    modelobj = Model.make_template()
    modelobj.beamlines['cantilever'].nelem = 20
    modelobj.beamlines['cantilever'].add_concentrated_load(
        node_uid='node_b',
        load=[0, 0, -1, 0, 0, 0],
    )

    settings = [
        ('plot_deformed', True),
        ('plot_bc', True),
        ('plot_nodes', True),
        ('set_savefig', True),
        ('plot_loads', True),
        ('plot_beamline_uids', True),
        ('plot_load_labels', True),
        ('plot_named_nodes', True),
        ('set_scale_conc_loads', 0.2),
        ('set_vectorwidth', 2),
        ('set_linewidth', 2),
    ]

    for key, value in settings:
        modelobj.postproc.plots[0][key] = value

    return modelobj
