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
Frame definition

Frame structure hierarchie::

    |   FRAME
    |     |
    | BEAMLINES
    |     |
    |  ELEMENTS
    |     |
    |   NODES
"""

from collections import defaultdict
import logging

import numpy as np
from scipy.interpolate import CubicSpline

from framat.fem.beamline import BeamLine
from framat.fem.element import Element
from framat.helpers.moresyntax import enumerate_with_step
import framat.fem.boundary_conditions as bc

logger = logging.getLogger(__name__)


class Frame:

    def __init__(self, beamline_definitions, bc_definitions, accel_definition, material_db, profile_db):
        """
        The frame is an assembly of multiple beams

        During init:
            * Global boundary conditions are applied
            * Global tensors are constructed

        Most notably, the frame object provides several global matrices
        which can be used for further analysis

            :K: Global stiffness matrix
            :M: Global mass matrix
            :U: Global deformation vector
            :F: Global load vector
            :B: Global boundary condition matrix

        Args:
            :beamlines: list of beamline objects
        """

        logger.info("Assembling frame structure...")

        self.is_assembled = False

        self.counter = ObjectCounter()
        self.finder = ObjectFinder()
        self.deformation = Deformation()
        self.boundary_conditions = BoundaryConditions()

        for bc_type, nodes in bc_definitions.items():
            self.boundary_conditions.add_boundary_condition(bc_type, nodes)

        self.material_db = material_db
        self.profile_db = profile_db

        # Generate beamline objects
        all_beamlines = []
        for beamline in beamline_definitions:
            new_beamline = BeamLine(**beamline, make_mirror=False, parent_frame=self)
            all_beamlines.append(new_beamline)

            if new_beamline.symmetry is not None:
                new_beamline = BeamLine(**beamline, make_mirror=True, parent_frame=self)
                all_beamlines.append(new_beamline)

        self.beamlines = all_beamlines
        self.ndof = None
        self.nnodes = None
        self.nelem = None
        self._update_discretisation()

        # Global tensors
        self.K = np.zeros((self.ndof, self.ndof))
        self.M = np.zeros((self.ndof, self.ndof))
        self.F = np.zeros((self.ndof, 1))
        self.B = None
        self.b = None

        # Acceleration vector (used to model gravity, for instance)
        self.accel_direction = np.array(accel_definition['direction'])
        self.accel_factor = accel_definition.get('accel_factor', 1)
        self.is_accelerated = accel_definition['turn_on']

        self.mass_breakdown = None
        self.work_breakdown = None

        self._apply_boundary_conditions()
        self._assemble_global_tensors()

    def __str__(self):
        return self.__class__.__name__ + f' object with {self.counter.nodes} nodes'

    def __repr__(self):
        return self.__str__()

    @property
    def accel_direction(self):
        if self.is_accelerated:
            return self.accel_factor*self._accel_direction
        else:
            return np.array([0, 0, 0])

    @accel_direction.setter
    def accel_direction(self, accel_direction):
        self._accel_direction = accel_direction

    @property
    def F_accel(self):
        """Loads due to inertia"""

        if not self.is_assembled:
            raise RuntimeError("Frame is not assembled")

        accel_vector = np.append(self.accel_direction, [0, 0, 0])
        accel = np.zeros((self.ndof, 1))
        accel[:, 0] = np.tile(accel_vector, self.nnodes)

        return self.M @ accel

    def _update_discretisation(self):
        """Update the discretisation parameters"""

        self.nelem = self.counter.elements
        self.nnodes = self.counter.nodes
        self.ndof = self.nnodes*Element.DOF_PER_NODE
        num_beams = self.counter.beams

        logger.info(f"Discretisation:")
        logger.info(f"--> n_beams: {num_beams:4d}")
        logger.info(f"--> n_elem:  {self.nelem:4d}")
        logger.info(f"--> n_nodes: {self.nnodes:4d}")
        logger.info(f"--> n_dof:   {self.ndof:4d}")

    def _apply_boundary_conditions(self):
        """Assemble the global boundary condition matrix"""

        logger.info("Assembling global boundary condition matrix...")

        self.B = np.array([])

        for bc_type, node_list in self.boundary_conditions.boundary_conditions.items():
            if bc_type == 'fix':
                for entry in node_list:
                    node_uid, dof_constraints = entry['node'], entry['fix']
                    node_num = self.finder.nodes.by_uid[node_uid].num

                    B = bc.fix_dof(node_num, self.ndof, dof_constraints)
                    self.B = np.vstack((self.B, B)) if self.B.size else B

            if bc_type == 'connect':
                for connection in node_list:
                    node1_uid = connection['node1']
                    node2_uid = connection['node2']
                    node1_number = self.finder.nodes.by_uid[node1_uid].num
                    node2_number = self.finder.nodes.by_uid[node2_uid].num

                    B = bc.connect(node1_number, node2_number, node1_uid, node2_uid, self.ndof, None, self)
                    self.B = np.vstack((self.B, B)) if self.B.size else B

        self.b = np.zeros((self.B.shape[0], 1))

    def _assemble_global_tensors(self):
        """
        Assemble global tensors:

            * Global stiffness matrix K
            * Global load vector F
        """

        logger.info("Assembling global stiffness matrix...")
        logger.info("Assembling global load matrix...")

        # Create a stiffness matrix for each beam
        K_per_beam = []
        M_per_beam = []
        F_per_beam = []
        for beamline in self.beamlines:
            K_beam = np.zeros((beamline.ndof, beamline.ndof))
            M_beam = np.zeros((beamline.ndof, beamline.ndof))
            F_beam = np.zeros((beamline.ndof, 1))

            for k, element in enumerate_with_step(beamline.elements, step=6):
                K_beam[k:k+12, k:k+12] += element.stiffness_matrix_glob
                M_beam[k:k+12, k:k+12] += element.mass_matrix_glob
                F_beam[k:k+12] += element.load_vector_glob

            K_per_beam.append(K_beam)
            M_per_beam.append(M_beam)
            F_per_beam.append(F_beam)

        # Paste each beam K matrix into global K
        paste_range = [0, 0]
        for K_beam, M_beam, F_beam in zip(K_per_beam, M_per_beam, F_per_beam):
            r = K_beam.shape[0]
            from_r = paste_range[1]
            to_r = from_r + r
            paste_range = [from_r, to_r]
            self.K[from_r:to_r, from_r:to_r] = K_beam
            self.M[from_r:to_r, from_r:to_r] = M_beam
            self.F[from_r:to_r] += F_beam

        self.is_assembled = True

    def get_mass_breakdown(self, enforce_recompute=False):
        """
        Return a mass breakdown of the frame structure

        Note:
            * Masses and centre of masses (CGs) of beamlines and entire frame
              are computed

        Args:
            :enforce_recompute: if True, the mass breakdown will be re-computed even if one already exists

        Returns:
            :mass_breakdown: dictionary containing a masses and CG positions
        """

        # If a mass breakdown exists, exit early
        if self.mass_breakdown and not enforce_recompute:
            return self.mass_breakdown

        logger.info("Computing a mass breakdown...")

        weighted_CG = np.array([0, 0, 0])  # Sum of [x_i, y_i, z_i]*element_mass_i
        total_mass = 0

        self.mass_breakdown = {"beams": {}}
        for beamline in self.beamlines:
            beam_CG, beam_mass = beamline.get_centre_of_mass()

            weighted_CG = weighted_CG + beam_mass*np.array(beam_CG)
            total_mass += beam_mass

            self.mass_breakdown["beams"][beamline.uid] = {"CG": beam_CG, "mass": beam_mass}
            logger.info(f"--> Beam '{beamline.uid:12s}': {beam_mass:.1e} kg at ({beam_CG[0]:8.1e}, {beam_CG[1]:8.1e}, {beam_CG[2]:8.1e})")

        coord_CG = weighted_CG/total_mass if total_mass != 0 else (0, 0, 0)

        self.mass_breakdown["total_CG"] = tuple(coord_CG)
        self.mass_breakdown["total_mass"] = total_mass
        logger.info(f"--> Total mass:        : {total_mass:.1e} kg at ({coord_CG[0]:8.1e}, {coord_CG[1]:8.1e}, {coord_CG[2]:8.1e})")

        return self.mass_breakdown

    def get_work_breakdown(self, enforce_recompute=False):
        """
        Return a work breakdown of the frame structure

        Args:
            :enforce_recompute: if True, the work breakdown will be re-computed
                even if one already exists

        Returns:
            :work_breakdown: dictionary containing a masses and the
        """

        # TODO: add work for each beam

        # If a work breakdown exists, exit early
        if self.work_breakdown and not enforce_recompute:
            return self.work_breakdown

        logger.info("Computing a work breakdown...")

        self.work_breakdown = {"beams": {}}

        U = self.deformation.U[:, 0]
        K = self.K

        W_total = 0.5*(U.T @ K @ U)

        self.work_breakdown['total_work'] = W_total

        return self.work_breakdown


class ObjectCounter:

    def __init__(self):
        """
        Book keeping class for the frame structure

        Counts beamlines, elements and nodes of a frame structure
        """

        self.elements = 0
        self.beams = 0

    @property
    def nodes(self):
        return self.elements + self.beams

    def increment_element_count(self):
        self.elements += 1

    def increment_beam_count(self):
        self.beams += 1

    def get_last_node_num(self):
        return self.nodes - 1


class ObjectFinder:

    def __init__(self):
        """
        Bookkeeping system

        Allows to find frame objects by UIDs or number
        """

        self.beamlines = self.BeamLines()
        self.elements = self.Elements()
        self.nodes = self.Nodes()

    class BeamLines:

        def __init__(self):
            self.by_uid = {}
            self.by_number = {}

        def update(self, beamline):
            self.by_uid.update({beamline.uid: beamline})
            self.by_number.update({beamline.num: beamline})

    class Elements:

        def __init__(self):
            self.by_number = {}

        def update(self, element_num, element):
            self.by_number.update({element_num: element})

    class Nodes:

        def __init__(self):
            self.by_uid = {}
            self.by_number = {}
            self.by_beamline_uid = defaultdict(list)

        def update(self, node):
            """
            Make a bookkeeping entry for a new node

            Note:
                * A new entry will only be created if :node: is first occurrence
                * If a node with same global number already exists, nothing is updated

            Args:
                :node: node object
            """

            if node.num not in self.by_number:
                node.is_primary = True
                self.by_number.update({node.num: node})
                self._add_beamline_node(node)

                if node.uid is not None:
                    if node.uid in self.by_uid:
                        raise RuntimeError(f"Unexpected attempt to add node '{node.uid}' to bookkeeping")

                    self._add_named_node(node)
            else:
                if (node.uid is not None) and (node.uid not in self.by_uid):
                    raise RuntimeError(f"Node '{node.uid}' not found in bookkeeping")

        def _add_named_node(self, node):
            self.by_uid.update({node.uid: node})

        def _add_beamline_node(self, node):
            self.by_beamline_uid[node.parent_beamline.uid].append(node)


class BoundaryConditions:

    def __init__(self):
        self.boundary_conditions = {}
        self.F_react = None

    def add_boundary_condition(self, bc_type, nodes):
        self.boundary_conditions.update({bc_type: nodes})

    def get_identifier(self, constraints):
        id_num = {'ux': 1, 'uy': 2, 'uz': 4, 'tx': 8, 'ty': 16, 'tz': 32, 'all': 63}

        bc_id = 0
        for constraint in constraints:
            bc_id += id_num[constraint]
            if bc_id == id_num['all']:
                break

        return bc_id


class Deformation:

    def __init__(self):
        self.U = None
        self.beamline_interpolators = defaultdict(lambda: None)

    def by_node_num(self, node_num, as_dict=False):
        """
        Return the nodal deformation based on the global node number
        """

        u = self.U[6*node_num:6*node_num+6, 0]

        if as_dict:
            return {key: u[i] for i, key in enumerate(Element.DEFORM_TYPES)}

        return u

    def get_beamline_interpolator(self, beamline_uid, frame):
        """
        Return an interpolator for the deformation along a beam line

        Note:
            * The interpolation function takes xsi (relative beamline
              coordinate) as an argument and return a 6x1 vector which
              contains the interpolated deformation (translations and
              rotations)

        Args:
            :beamline_uid: UID of the beamline

        Returns:
            :def_interpolator: interpolation function
        """

        interpolator = self.beamline_interpolators[beamline_uid]

        if interpolator is not None:
            return interpolator

        deformation = defaultdict(list)
        xsi_values = []

        # TODO: can be improved (all beam nodes in one line)
        for node in frame.finder.nodes.by_beamline_uid[beamline_uid]:
            nodal_deform = self.by_node_num(node.num, as_dict=True)
            xsi_values.append(node.xsi)
            for key in Element.DEFORM_TYPES:
                deformation[key].append(nodal_deform[key])

        interpol = {}
        for key in Element.DEFORM_TYPES:
            interpol[key] = CubicSpline(xsi_values, deformation[key])

        def def_interpolator(xsi):
            def_list = np.array([interpol[key](xsi) for key in Element.DEFORM_TYPES])
            return def_list

        self.beamline_interpolators[beamline_uid] = def_interpolator
        return def_interpolator

    def get_displacement_fields(self, frame, n_sup=20):
        """
        Returns beam displacement field

        Args:
            :frame: Frame object
            :n_sup: Number of support points (linearly spaced along the beam)

        Returns:
            :displacement_fields: Dictionary with arrays of displacement fields

        Example:

        For a frame with two beamlines, say 'main_wing' and 'fuselage', a dictionary
        with the following form will be created:

        .. code:: python

            displacement_fields = {
                'main_wing': array([
                    [x1, y1, z1, ux1, uy1, uz1, tx1, ty1, tz1],
                    [x2, y2, z2, ux2, uy2, uz2, tx2, ty2, tz2],
                    ...
                    [x3, y3, z3, ux3, uy3, uz3, tx3, ty3, tz3],
                ]),
                'fuselage': array([
                    [x1, y1, z1, ux1, uy1, uz1, tx1, ty1, tz1],
                    [x2, y2, z2, ux2, uy2, uz2, tx2, ty2, tz2],
                    ...
                    [x3, y3, z3, ux3, uy3, uz3, tx3, ty3, tz3],
                ]),
            }
        """

        displacement_fields = {}
        for beamline in frame.beamlines:
            def_interpolator = self.get_beamline_interpolator(beamline.uid, frame)
            displacement_fields[beamline.uid] = np.zeros((n_sup, 9))
            for i, xsi in enumerate(np.linspace(0, 1, num=n_sup)):
                point = beamline.interpolator(xsi)
                def_vec = def_interpolator(xsi)
                entry = np.concatenate([point, def_vec])
                displacement_fields[beamline.uid][i, :] = entry
        return displacement_fields
