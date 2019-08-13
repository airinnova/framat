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
Beamline
"""

# Author: Aaron Dettmann

from collections import defaultdict
from copy import copy
import logging

import numpy as np
from scipy.interpolate import CubicSpline

from framat.fem.element import Element
from framat.fem.element import GlobalSystem as GS
from framat.fem.interpolate import PointInterpolator, PropertyInterpolator
from framat.helpers.iterators import pairwise
from commonlibs.mathtools.vectors import rotate_vector_around_axis

logger = logging.getLogger(__name__)

INFINITY = 1e100


class ComponentDefinitionError(Exception):
    pass


class BeamLine:

    GET_CLOSEST_NODE = '__GET_CLOSEST_NODE'
    GET_CLOSEST_X = '__GET_CLOSEST_X'
    GET_CLOSEST_Y = '__GET_CLOSEST_Y'
    GET_CLOSEST_Z = '__GET_CLOSEST_Z'

    FINDER_KEYWORDS = [GET_CLOSEST_NODE,
                       GET_CLOSEST_X, GET_CLOSEST_Y, GET_CLOSEST_Z]

    def __init__(self, uid, nodes, nelem, beamprops, loads=None,
                 perimeter_lines=None, symmetry=None, make_mirror=False,
                 mirror_loads=None, mirror_beamprops=None, parent_frame=None,
                 free_node_mapping=None):
        """
        Beam line object (line in 3D space)

        Args:
            :uid: UID of the beam line (None if not defined)
            :nodes: list of dicts with named node
            :nelem: number of desired nodes (number will be approximated)
            :beamprops: properties which are to be assigned to the beam
            :loads: external loads acting on the beam
            :symmetry: symmetry plane
            :mirror: flag stating if instance is a mirrored or not
        """

        logger.debug(f"Adding new beam '{uid}'...")

        # Base attributes
        self.uid = uid
        self.named_nodes = nodes
        self.input_nelem = nelem
        self.beamprops = beamprops
        self.loads = loads
        self.perimeter_lines = perimeter_lines
        self.symmetry = symmetry
        self.mirror = make_mirror
        self.parent_frame = parent_frame

        if free_node_mapping is None:
            # Map free node loads by default to the closest node
            self.free_node_mapping = self.GET_CLOSEST_NODE
        else:
            if free_node_mapping not in self.FINDER_KEYWORDS:
                raise ValueError("Unknown free node mapping scheme")

            logger.info(f"Default free node mapping scheme: '{free_node_mapping}'")
            self.free_node_mapping = free_node_mapping

        # Mirror a beam across a symmetry plane
        if self.mirror is True:
            if self.symmetry is None:
                raise ComponentDefinitionError("Beam line has no symmetry plane")

            if mirror_loads is None:
                self.has_mirror_loads = False
            else:
                self.has_mirror_loads = True
                self.loads = mirror_loads

            if mirror_beamprops is None:
                self.has_mirror_beamprops = False
            else:
                self.has_mirror_beamprops = True
                self.beamprops = mirror_beamprops

            self._mirror_beamline()

        # Book keeping
        self.num = self.parent_frame.counter.beams
        self.parent_frame.counter.increment_beam_count()
        self.parent_frame.finder.beamlines.update(self)

        # Point interpolator
        point_list = []
        uid_list = []
        for node in self.named_nodes:
            point_list.append(np.array(node['coord']))
            uid_list.append(node['uid'])

        self.interpolator = PointInterpolator(point_list, uid_list)

        # List of child objects
        self.elements = []
        self.free_nodes = []
        self.perimeter_line_list = []

        self._make_elements()
        self._add_beam_properties()
        self._add_loads()
        self._make_perimeter_lines()

    def __repr__(self):
        return self.__class__.__name__ + f" '{self.uid}' (no. {self.num})"

    def __str__(self):
        return self.__class__.__name__ + f" '{self.uid}' (no. {self.num})"

    @property
    def length(self):
        """Beamline length"""

        return self.interpolator.length

    @property
    def nelem(self):
        """Number of elements"""

        return len(self.elements)

    @property
    def nnodes(self):
        """Number of nodes"""

        return self.nelem + 1

    @property
    def ndof(self):
        """Number of nodes"""

        return self.nnodes*Element.DOF_PER_NODE

    @property
    def nodes(self):
        """Nodes of the beamline instance"""

        return self.parent_frame.finder.nodes.by_beamline_uid[self.uid]

    def get_point(self, xsi):
        """
        Return coordinate of a beam point based on a line coordinate xsi

        Args:
            :xsi: relative coordinate in range [0, 1]

        Returns:
            :coord: x, y, z coordinates
        """

        if not (0 <= xsi <= 1):
            raise ValueError("xsi must be in range [0, 1]")

        return self.interpolator(xsi)

    def _make_elements(self):
        """Create element objects constituting the beam line object"""

        # Make an interpolator for up
        up_for_named_nodes = []
        for node in self.named_nodes:
            up_for_named_nodes.append(node['up'])

        xsi_named_nodes = self.interpolator.get_xsi_support_points()
        up = PropertyInterpolator(xsi_named_nodes, up_for_named_nodes)

        # Get list of (relative) points for element nodes
        point_list = self.interpolator.get_n_points(self.input_nelem + 1)

        for point1, point2 in pairwise(point_list):
            xsi1 = point1.xsi
            xsi2 = point2.xsi
            xsi = (xsi1 + xsi2)/2

            uid1 = point1.uid
            uid2 = point2.uid

            new_element = Element(self, xsi1, xsi2, uid1, uid2, up=up(xsi, 'prev'))
            self.elements.append(new_element)

    def _add_beam_properties(self):
        """Assign beam properties to elements"""

        logger.debug(f"Assigning beam properties to beam '{self.uid}'...")

        # ===== RANGE PROPERTIES =====
        for entry in self.beamprops:
            # Skip 'single node properties'
            if entry.get('at', None) is not None:
                continue

            from_node = entry['from']
            to_node = entry['to']

            from_xsi = self.parent_frame.finder.nodes.by_uid[from_node].xsi
            to_xsi = self.parent_frame.finder.nodes.by_uid[to_node].xsi

            logger.debug(f"--> from: '{from_node}' (xsi={from_xsi:.2f}) to: '{to_node}' (xsi={to_xsi:.2f})...")

            # ----- Constant properties -----
            if entry.get('constant', None) is not None:
                material = self.parent_frame.material_db.by_uid[entry['constant']['material']]
                profile = self.parent_frame.profile_db.by_uid[entry['constant']['profil']]

                properties = {}
                properties.update(material)
                properties.update(profile)

                for element in self.elements:
                    if from_xsi <= element.node2.xsi <= to_xsi:
                        element.update_properties(properties)

            # ----- Varying properties -----
            prop_list = entry.get('vary', None)
            if prop_list is not None:
                prop = self._get_property_interpolator(prop_list,
                                                       from_xsi,
                                                       to_xsi,
                                                       Element.PROP_TYPES,
                                                       warn_negative=False)

                for element in self.elements:
                    xsi = (element.node1.xsi + element.node2.xsi)/2
                    if from_xsi <= xsi <= to_xsi:
                        element.update_properties(prop(xsi))

            # ----- Distribute mass over a range of elements -----
            if entry.get('mass', None) is not None:
                logger.debug(f"Attaching total mass of {entry['mass']:.2e} kg...")

                # Adding negative masses can be useful to calibrate a beam mass,
                # but a warning should be given at least
                if entry['mass'] < 0:
                    logger.warning(f"--> Adding NEGATIVE mass {entry['mass']:.2e} kg...")

                node_list = []
                for node in self.parent_frame.finder.nodes.by_beamline_uid[self.uid]:
                    if from_xsi <= node.xsi <= to_xsi:
                        node_list.append(node)

                num_nodes = len(node_list)
                mass_per_node = entry['mass']/num_nodes

                for node in node_list:
                    logger.debug(f"--> Attaching mass of {mass_per_node:.2e} kg to node '{node.num}'...")
                    node.parent_element.add_pointmass(mass_per_node, node.elem_loc)

        # ===== SINGLE NODE PROPERTIES =====
        for entry in self.beamprops:
            # Skip 'range properties'
            if entry.get('at', None) is None:
                continue

            at_node = entry['at']
            pointmass = entry['pointmass']

            target_node = None
            for element in self.elements:
                if element.node1.uid == at_node:
                    target_node = element.node1
                elif element.node2.uid == at_node:
                    target_node = element.node2

                if target_node is not None:
                    element = target_node.parent_element
                    elem_loc = target_node.elem_loc

                    logger.debug(f"Attaching pointmass of {pointmass:.2e} kg to node '{at_node}'...")
                    element.add_pointmass(pointmass, elem_loc)
                    break
            else:
                raise RuntimeError(f"Node '{at_node}' not found on beam '{self.uid}'")

    def _add_loads(self):
        """Assign loads to elements"""

        logger.debug(f"Assigning beam loads to beam '{self.uid}'...")

        loads = self.loads

        if loads is None:
            return

        if loads.get('concentrated', False):
            for entry in loads['concentrated']:
                node_uid = entry['node']
                load = entry['load']
                loads_in_loc_system = entry.get('in_local_system', False)

                node = self.parent_frame.finder.nodes.by_uid.get(node_uid, None)
                if node is None:
                    continue

                # TODO: check node in beam

                load = self.load_as_dict(load, Element.CONC_LOAD_BASE_TYPES)
                element = node.parent_element
                element.update_concentrated_loads(load, node.elem_loc, loads_in_loc_system)

        if loads.get('distributed', False):
            for entry in loads['distributed']:
                from_node = entry['from']
                to_node = entry['to']
                loads_in_loc_system = entry.get('in_local_system', False)

                # TODO: check node in beam

                node = self.parent_frame.finder.nodes.by_uid.get(from_node, None)
                if node is None:
                    continue
                if node.parent_beamline is not self:
                    continue

                from_xsi = self.parent_frame.finder.nodes.by_uid[from_node].xsi
                to_xsi = self.parent_frame.finder.nodes.by_uid[to_node].xsi

                # ===== Constant loads =====
                load = entry.get('constant', None)
                if load is not None:
                    load = self.load_as_dict(load, Element.DIST_LOAD_TYPES)

                    for element in self.elements:
                        if from_xsi < element.mid_xsi < to_xsi:
                            element.update_distributed_loads(load, loads_in_loc_system)

                # ===== Varying loads =====
                load_list = entry.get('vary', None)
                if load_list is not None:
                    load = self._get_dist_load_interpolator(load_list, from_xsi, to_xsi, Element.DIST_LOAD_TYPES)

                    for element in self.elements:
                        xsi = (element.node1.xsi + element.node2.xsi)/2
                        if from_xsi <= xsi <= to_xsi:
                            element.update_distributed_loads(load(xsi), loads_in_loc_system)

        # ===== Loads from free nodes =====
        if loads.get('free_nodes', False):
            for entry in loads['free_nodes']:
                fn_coord = np.array(entry['coord'])
                fn_load = np.array(entry['load'])

                # Destination node may be specified
                dest_node = entry.get('node', None)
                if dest_node in BeamLine.FINDER_KEYWORDS:
                    dest_node, _ = self.get_closest_beam_node(fn_coord, search=dest_node)
                elif dest_node is not None:
                    dest_node = self.parent_frame.finder.nodes.by_uid[dest_node]
                else:
                    dest_node, _ = self.get_closest_beam_node(fn_coord, search=self.free_node_mapping)

                load_proj = self.project_load(fn_load, fn_coord, dest_node.coord)

                entry["closest_beam_node"] = dest_node
                self.free_nodes.append(copy(entry))

                # Apply load
                load_proj = self.load_as_dict(load_proj, Element.CONC_LOAD_BASE_TYPES)
                elem_loc = dest_node.elem_loc
                element = dest_node.parent_element
                element.update_concentrated_loads(load_proj, elem_loc, is_loc_system=False)

    def _make_perimeter_lines(self):
        """
        Make perimeter lines
        """

        if self.perimeter_lines is not None:
            for line in self.perimeter_lines:
                self.perimeter_line_list.append(PerimeterLine(self, line))

    @staticmethod
    def _get_dist_load_interpolator(load_list, from_xsi, to_xsi, keys):
        """
        Return a function that generates a load dictionary for a given
        beam line position (xsi)

        :Note:
            * The load interpolator returns a function which takes the
              "beam global" 'xsi' coordinate as an argument (and not 's')

        Args:
            :loads_list: list with dicts (keys: 's' and 'load')

        Returns:
            :load_interpolator: function with argument xsi (returns interpolated distributed loads)
        """

        # TODO: combine with _get_property_interpolator, make both functions expect dicts

        s = []
        load_points = defaultdict(list)

        for entry in load_list:
            s.append(entry['s'])

            for i, key in enumerate(keys):
                load_points[key].append(entry['load'][i])

        interpol = {}
        for key in keys:
            interpol[key] = CubicSpline(s, load_points[key])

        def prop_interpolator(xsi):
            s = (xsi - from_xsi)/(to_xsi - from_xsi)
            load_dict = {key: interpol[key](s) for key in keys}

            return load_dict

        return prop_interpolator

    @staticmethod
    def _get_property_interpolator(prop_list, from_xsi, to_xsi, keys, warn_negative=False):
        """
        Return a function that generates a beam property dictionary for a
        given beam line position (xsi)

        :Note:
            * The load interpolator returns a function which takes the
              "beam global" 'xsi' coordinate as an argument (and not 's')

        Args:
            :prop_list: list with dicts (keys: 's' and 'load')

        Returns:
            :prop_interpolator: function with argument xsi (returns interpolated properties)
        """

        # TODO: add warning if any values negative

        s = []
        prop_points = defaultdict(list)
        for entry in prop_list:
            s.append(entry['s'])

            for key in keys:
                prop_points[key].append(entry[key])

        interpol = {}
        for key in keys:
            interpol[key] = CubicSpline(s, prop_points[key])

        def prop_interpolator(xsi):
            s = (xsi - from_xsi)/(to_xsi - from_xsi)
            prop_dict = {key: interpol[key](s) for key in keys}

            if warn_negative:
                for key, value in prop_dict.items():
                    if value < 0:
                        logger.warning(f"Negative value: {key}={value:.2e} (xsi={xsi:.2f})")

            return prop_dict

        return prop_interpolator

    def _mirror_beamline(self):
        """
        Mirror a beamline based on a symmetry plane

        * The beam geometry (nodes and direction is fully mirrored)
        * A suffix is added to all UIDs (for the beam line itself and for all nodes)
        * By default:
            * Beam properties are fully mirrored
            * Loads are fully mirrored
        * If beam properties or loads are to be assymetric, they have to be
          explicitly provided
        """

        logger.info(f"Creating {self.symmetry}-mirror for '{self.uid}'...")

        uid_suffix = "_m"
        self.uid += uid_suffix

        # ===== GEOMETRY =====
        # Modify nodes
        for node in self.named_nodes:
            node['uid'] += uid_suffix
            node['coord'] = mirror_point(node['coord'], self.symmetry)
            node['up'] = mirror_point(node['up'], self.symmetry)

        # Modify perimeter lines
        if self.perimeter_lines is not None:
            for line in self.perimeter_lines:
                line['uid'] += uid_suffix
                line['from']['coord'] = mirror_point(line['from']['coord'], self.symmetry)
                line['to']['coord'] = mirror_point(line['to']['coord'], self.symmetry)

                if line['from']['node'].upper() not in PerimeterLine.SPECIAL_KEYWORDS:
                    line['from']['node'] += uid_suffix

                if line['to']['node'].upper() not in PerimeterLine.SPECIAL_KEYWORDS:
                    line['to']['node'] += uid_suffix

        # ===== BEAM PROPERTIES =====
        if not self.has_mirror_beamprops:
            # Modify properties
            for entry in self.beamprops:
                for k in ['from', 'to', 'at']:
                    if entry.get(k, False):
                        entry[k] += uid_suffix

        # ===== LOADS =====
        if not self.has_mirror_loads:
            logger.info("No mirror loads provided. Mirroring loads...")

            if self.loads is None:
                logger.warning("--> Main beam has no loads to mirror... Exit.")
                return

            # Modify concentrated loads
            if self.loads.get('concentrated', None) is not None:
                for entry in self.loads['concentrated']:
                    entry['node'] += uid_suffix
                    entry['load'] = self.mirror_load(entry['load'], self.symmetry)

            # Modify distributed loads
            if self.loads.get('distributed', None) is not None:
                for entry in self.loads['distributed']:
                    entry['from'] += uid_suffix
                    entry['to'] += uid_suffix

                    if entry.get('constant', None) is not None:
                        entry['constant'] = self.mirror_load(entry['constant'], self.symmetry)
                    elif entry.get('vary', None) is not None:
                        for line in entry['vary']:
                            line['load'] = self.mirror_load(line['load'], self.symmetry)

            # Modify free node loads
            if self.loads.get('free_nodes', None) is not None:
                for entry in self.loads['free_nodes']:
                    entry['coord'] = mirror_point(entry['coord'], self.symmetry)
                    entry['load'] = self.mirror_load(entry['load'], self.symmetry)

                    if entry.get('node', False):
                        entry['node'] += uid_suffix

    def get_closest_beam_node(self, point_coord, in_range=(0, 1), search=GET_CLOSEST_NODE):
        """
        Return closest node on beamline given a point in space

        Args:
            :point_coord: coordinates of point
            :in_range: restrict search to beamline range (0, 1)
            :search: scheme for node search

        Returns:
            :closest_node: closest beam node
            :distance: distance to closest beam node
        """

        xsi_min, xsi_max = in_range
        closest_dist = INFINITY
        closest_node = None

        # Dictionary with different search patterns
        dist_func = {
            self.GET_CLOSEST_NODE: lambda x, y: np.linalg.norm(x - y),
            self.GET_CLOSEST_X: lambda x, y: abs(x[0] - y[0]),
            self.GET_CLOSEST_Y: lambda x, y: abs(x[1] - y[1]),
            self.GET_CLOSEST_Z: lambda x, y: abs(x[2] - y[2]),
        }

        # Assign search function
        get_dist = dist_func[search]

        for node in self.parent_frame.finder.nodes.by_beamline_uid[self.uid]:
            if not (xsi_min <= node.xsi <= xsi_max):
                continue

            dist = get_dist(point_coord, node.coord)
            if dist < closest_dist:
                closest_dist = dist
                closest_node = node

        if closest_node is None:
            raise RuntimeError("No closest node found")

        return closest_node, closest_dist

    @staticmethod
    def project_load(load, from_point, to_point):
        """
        Project a concentrated load from one point onto another

        Args:
            :load: concentrated load which is to be projected
            :from_point: point at which 'load' acts
            :to_point: point onto which 'load' is to be projected

        Returns:
            :load_proj: projected load
        """

        # r: vector pointing from projection point to load source
        load = np.array(load)
        from_point = np.array(from_point)
        to_point = np.array(to_point)
        force = load[0:3]
        r = from_point - to_point

        load_proj = np.zeros((6))
        load_proj += load
        load_proj[3:6] += np.cross(r, force)
        return load_proj

    @staticmethod
    def load_as_dict(input_load, keys):
        """
        Convert concentrated or distributed loads to a dictionary with
        specified keys

        Note:
            * If the input is a dict, missing keys will be added with default
              values of zero

        Args:
            :input_load: loads in form of a dict or list
            :keys: names/keys of loads

        Returns:
            :load: loads converted to a dict
        """

        load = {}

        for i, key in enumerate(keys):
            load[key] = input_load[i]

        return load

    @staticmethod
    def mirror_load(load, plane):
        """
        Mirror loads across a symmetry plane

        Args:
            :load: "sliceable" load with length (6x1)
            :plane: symmetry plane

        Returns:
            :mirrored_loads: mirrored loads
        """

        load[0:3] = mirror_point(load[0:3], plane)
        load[3:6] = mirror_point(load[3:6], plane)
        return load

    def get_deformation(self, xsi):
        """
        Return the beamline deformation at xsi

        Args:
            :xsi: relative coordinate in range [0, 1]

        Returns:
            :U_b: deformation
        """

        def_interpolator = self.parent_frame.deformation.get_beamline_interpolator(self.uid, self.parent_frame)
        return np.array(def_interpolator(xsi))

    def get_deformation_of_point(self, point, in_range=(0, 1), use_xsi=None):
        """
        Return the deformation of a point which does not lie on the beam line

        By default the deformation at the point in interpolated based on the
        nearest beam node. If the parameter 'use_xsi' is given, this xsi
        value is used instead.

        Args:
            :point: point at which deformation is to be interpolated
            :in_range: xsi range (closest beam line point will be restricted to xsi range)
            :use_xsi: use a specified xsi position (default is nearest node)

        Returns:
            :deformation: relative deformation at point
        """

        # If beam xsi position is specified, use it
        if use_xsi is not None:
            if not (0 <= use_xsi <= 1):
                raise ValueError("use_xsi must be in range [0, 1]")

            U_b = self.get_deformation(use_xsi)
            beam_point = self.get_point(use_xsi)
        # If beam xsi position is not specified, use nearest node position
        else:
            node, _ = self.get_closest_beam_node(point, in_range)
            U_b = self.get_deformation(node.xsi)
            beam_point = node.coord

        # Deformation on the target (p)oint
        U_p = np.zeros((6))
        U_p += U_b

        # Additional translation due to point being a distance r away from beam point
        r = point - beam_point

        r_rot = copy(r)
        r_rot = rotate_vector_around_axis(r_rot, GS.UnitVectors.X, U_b[3])
        r_rot = rotate_vector_around_axis(r_rot, GS.UnitVectors.Y, U_b[4])
        r_rot = rotate_vector_around_axis(r_rot, GS.UnitVectors.Z, U_b[5])
        U_p[0:3] += r_rot - r

        return U_p

    def get_nodes_by_xsi(self, xsi):
        """
        Get a beam node for a given xsi position

        Args:
            :xsi: relative coordinate in range [0, 1]

        Returns:
            :next_node, prev_node: next and previous node
        """

        for prev_node, next_node in pairwise(self.nodes):
            if prev_node.xsi <= xsi <= next_node.xsi:
                return prev_node, next_node

        return None, None

    def get_centre_of_mass(self):
        """
        Return the centre of mass (CG) and the total mass of the beamline

        Notes:
            * Returns a CG = (0, 0, 0) if the total mass is zero

        Returns:
            :coord_CG: tuple with x, y and z coordinate of the CG
            :total_mass: total mass of the frame structure
        """

        weighted_CG = np.array([0, 0, 0])  # Sum of [x_i, y_i, z_i]*element_mass_i
        total_mass = 0

        for element in self.elements:
            element_mass = element.mass

            weighted_CG = weighted_CG + element_mass*element.mid_point
            total_mass += element_mass

        coord_CG = weighted_CG/total_mass if total_mass != 0 else (0, 0, 0)
        return tuple(coord_CG), total_mass


def mirror_point(point, plane):
    """
    Mirror a point in 3D space about a symmetry plane.

    Args:
        :point: point
        :plane: (str) plane ('xy', 'xz' or 'yz')
    """

    point = copy(point)
    plane = plane.lower()

    if plane == 'xy' or plane == 1:
        point[2] = -point[2]
    elif plane == 'xz' or plane == 2:
        point[1] = -point[1]
    elif plane == 'yz' or plane == 3:
        point[0] = -point[0]
    else:
        raise ValueError("Invalid plane (plane: {})".format(plane))

    return point


class PerimeterLine:

    GET_CLOSEST_NODE = '__GET_CLOSEST_NODE'
    SPECIAL_KEYWORDS = [GET_CLOSEST_NODE]

    def __init__(self, beamline, perimeter_line):
        """
        Perimeter lines are optional child objects of beamline objects

        Perimeter lines provide a geometric interpolation method. They can
        be used to track the deformation of a line at some distance away from
        the actual elastic beam axis.

        Args:
            :beamline: parent beamline object
            :perimeter_line: data to generate the perimeter line

        Attributes:
            :uid: name of the perimeter line
            :p1: coordinates of the first line point
            :p2: coordinates of the second line point
            :node1: first border
            :node2: second border
        """

        self.parent_beamline = beamline
        self.parent_frame = self.parent_beamline.parent_frame

        self.uid = perimeter_line['uid']
        self.p1 = perimeter_line['from']['coord']
        self.p2 = perimeter_line['to']['coord']

        # Names of nodes to which perimeter line is to be connected
        self.node1_uid = perimeter_line['from']['node']
        self.node2_uid = perimeter_line['to']['node']

        # Get references to nodes one and two
        if self.node1_uid.upper() == self.GET_CLOSEST_NODE:
            self.node1, _ = self.parent_beamline.get_closest_beam_node(self.p1)
            logger.debug(f"Perimeter line '{self.uid}': using closest node {self.node1.num} for point 1")
        else:
            self.node1 = self.parent_frame.finder.nodes.by_uid[self.node1_uid]

        if self.node2_uid.upper() == self.GET_CLOSEST_NODE:
            self.node2, _ = self.parent_beamline.get_closest_beam_node(self.p2)
            logger.debug(f"Perimeter line '{self.uid}': using closest node {self.node2.num} for point 2")
        else:
            self.node2 = self.parent_frame.finder.nodes.by_uid[self.node2_uid]

        self.interpolator = PointInterpolator((self.p1, self.p2))

    def get_point(self, s):
        """
        Return a point on the perimeter line

        Args:
            :s: relative line coordinate [0, 1]

        Returns:
            :point: point on the perimeter line
        """

        return self.interpolator(s)

    def get_deformation(self, s, same_rel_position=True):
        """
        Get the deformation for a point on the perimeter line

        Args:
            :s: relative line coordinate [0, 1]

        Returns:
            :def_point: deformed point on the perimeter line
        """

        point = self.get_point(s)

        node1 = self.parent_frame.finder.nodes.by_number[self.node1.num]
        node2 = self.parent_frame.finder.nodes.by_number[self.node2.num]
        in_range = (node1.xsi, node2.xsi)

        if same_rel_position:
            xsi = node1.xsi + s*(node2.xsi - node1.xsi)
            return self.parent_beamline.get_deformation_of_point(point, in_range, use_xsi=xsi)
        else:
            return self.parent_beamline.get_deformation_of_point(point, in_range)
