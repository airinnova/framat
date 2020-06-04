#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Copyright 2019-2020 Airinnova AB and the FramAT authors
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
Beam element definition
"""

from collections import defaultdict
import logging

import numpy as np
from commonlibs.math.vectors import unit_vector, direction_cosine, vector_rejection

logger = logging.getLogger(__name__)


class GlobalSystem:
    Origin = np.array([0, 0, 0])
    X = np.array([1, 0, 0])
    Y = np.array([0, 1, 0])
    Z = np.array([0, 0, 1])


G = GlobalSystem


def get_local_system_from_up(x_elem, up):
    """
    Return the y- and z-axis of a Cartesian coordinate system (local element
    coordinate system) for a given x-axis and a defined "up-direction"

    Args:
        :x_elem: x-axis (of the element)
        :up: up-direction

    Returns:
        :y_axis: y-axis
        :z_axis: z-axis

    * Values are returned as a tuple
    """

    if abs(1 - abs(np.dot(x_elem, up))) <= 1e-10:
        logger.error("up-direction and local x-axis are parallel")
        raise ValueError("up-direction and local x-axis are parallel")

    z_elem = unit_vector(vector_rejection(up, x_elem))
    y_elem = unit_vector(np.cross(z_elem, x_elem))
    return (y_elem, z_elem)


class Element:
    """
    Euler-Bernoulli element with 6 degrees of freedom

    Nomenclature

    Material properties:
        :E: Young's modulus [N/m²]
        :G: Shear modulus [N/m²]
        :rho: Material density [kg/m³]

    Cross section properties:
        :A: Cross section area [m²]
        :Iy: Second moment of area about element local y-axis [m⁴]
        :Iz: Second moment of area about element local z-axis [m⁴]
        :J: Torsional constant [m⁴]

    Inertia properties:
        :m{1,2}: Point mass attached to node 1 or 2 [kg]

    Loads:
        F{x,y,z}{1,2}: Point load in x,y,z-directions applied to node 1 or 2 [N]
        M{x,y,z}{1,2}: Point moment in x,y,z-directions applied to node 1 or 2 [N]
        q{x,y,z}: Line force in x,y,z-directions applied to length of element [N/m]
        m{x,y,z}: Line moment in x,y,z-directions applied to length of element [N*m/m]

    Deformation:
        u{x,y,z}{1,2}: Displacement in x,y,z-direction (in global system) [m]
        t{x,y,z}{1,2}: Rotation in x,y,z-direction (in global system) [rad]
    """

    DOF_PER_NODE = 6

    MATERIAL_PROPS = ('E', 'G', 'rho')
    CROSS_SECTION_PROPS = ('A', 'Iy', 'Iz', 'J')
    PROP_TYPES = MATERIAL_PROPS + CROSS_SECTION_PROPS

    POINT_PROPS = ('m1', 'm2')

    DEFORM_TYPES = ('ux', 'uy', 'uz', 'tx', 'ty', 'tz')
    DIST_LOAD_TYPES = ('qx', 'qy', 'qz', 'mx', 'my', 'mz')
    CONC_LOAD_BASE_TYPES = ('Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz')
    CONC_LOAD_TYPES = ('Fx1', 'Fy1', 'Fz1', 'Mx1', 'My1', 'Mz1',
                       'Fx2', 'Fy2', 'Fz2', 'Mx2', 'My2', 'Mz2')

    def __init__(self, p1, p2, up):
        """
        Beam finite element with 6 dof per node

        TODO
        """

        # ===== Geometry =====
        # Node points
        self.p1 = p1
        self.p2 = p2

        # Vectors of the local coordinate system
        self.x_elem = unit_vector(self.p2.coord - self.p1.coord)
        self.y_elem, self.z_elem = get_local_system_from_up(self.x_elem, up)

        # Additional geometric properties
        self.mid_point = (self.p1.coord + self.p2.coord)/2
        self.mid_xsi = (self.p1.rel_coord + self.p2.rel_coord)/2
        self.length = np.linalg.norm(self.p2.coord - self.p1.coord)

        # ===== Material and cross section properties =====
        self.properties = defaultdict(lambda: None)

        # ===== Load vector in the global system =====
        self.load_vector_glob = np.zeros((12, 1))
        self.mass_matrix_glob = np.zeros((12, 12))
        self.stiffness_matrix_glob = np.zeros((12, 12))

        # ===== Transformation matrix =====
        lx = direction_cosine(self.x_elem, G.X)
        ly = direction_cosine(self.y_elem, G.X)
        lz = direction_cosine(self.z_elem, G.X)
        mx = direction_cosine(self.x_elem, G.Y)
        my = direction_cosine(self.y_elem, G.Y)
        mz = direction_cosine(self.z_elem, G.Y)
        nx = direction_cosine(self.x_elem, G.Z)
        ny = direction_cosine(self.y_elem, G.Z)
        nz = direction_cosine(self.z_elem, G.Z)

        T3 = np.array([[lx, mx, nx], [ly, my, ny], [lz, mz, nz]])
        self.T = np.zeros((12, 12))
        self.T[0:3, 0:3] = self.T[3:6, 3:6] = self.T[6:9, 6:9] = self.T[9:12, 9:12] = T3

    @classmethod
    def from_abstract_element(cls, a):
        """Create an new element from an abstract beam element"""

        new = cls(a.p1, a.p2, a.get('up'))

        for prop_type in new.PROP_TYPES:
            new.properties[prop_type] = a.get(prop_type)

        # Update mass and stiffness matrices from material and cross section properties
        new.update_element_stiffness_matrix()
        new.update_element_mass_matrix()

        for d in a.iter('point_load'):
            new.add_point_load(d['load'], d['node'], d.get('loc_system', False))

        for d in a.iter('point_mass'):
            new.add_point_mass(d['mass'], d['node'])

        for d in a.iter('distr_load'):
            new.add_distr_load(d['load'], d.get('loc_system', False))

        return new

    @property
    def stiffness_matrix_local(self):
        """Element stiffness matrix (as formulated in local system)"""

        E = self.properties['E']
        G = self.properties['G']
        A = self.properties['A']
        Iy = self.properties['Iy']
        Iz = self.properties['Iz']
        J = self.properties['J']

        EA = E*A
        EIy = E*Iy
        EIz = E*Iz
        GJ = G*J
        L = self.length
        L2 = L**2
        L3 = L**3

        k_elem = np.zeros((12, 12))

        k_elem[0, 0] = EA/L
        k_elem[0, 6] = -EA/L
        k_elem[1, 1] = 12*EIz/L3
        k_elem[1, 5] = 6*EIz/L2
        k_elem[1, 7] = -12*EIz/L3
        k_elem[1, 11] = 6*EIz/L2
        k_elem[2, 2] = 12*EIy/L3
        k_elem[2, 4] = -6*EIy/L2
        k_elem[2, 8] = -12*EIy/L3
        k_elem[2, 10] = -6*EIy/L2
        k_elem[3, 3] = GJ/L
        k_elem[3, 9] = -GJ/L
        k_elem[4, 4] = 4*EIy/L
        k_elem[4, 8] = 6*EIy/L2
        k_elem[4, 10] = 2*EIy/L
        k_elem[5, 5] = 4*EIz/L
        k_elem[5, 7] = -6*EIz/L2
        k_elem[5, 11] = 2*EIz/L
        k_elem[6, 6] = EA/L
        k_elem[7, 7] = 12*EIz/L3
        k_elem[7, 11] = -6*EIz/L2
        k_elem[8, 8] = 12*EIy/L3
        k_elem[8, 10] = 6*EIy/L2
        k_elem[9, 9] = GJ/L
        k_elem[10, 10] = 4*EIy/L
        k_elem[11, 11] = 4*EIz/L

        k_elem += np.triu(k_elem, k=1).T
        return k_elem

    def update_element_stiffness_matrix(self):
        """Element stiffness matrix (transformed to global system)"""

        k_elem = self.stiffness_matrix_local
        k_glob = self.T.T @ k_elem @ self.T
        self.stiffness_matrix_glob += k_glob

    @property
    def mass_matrix_local(self):
        """Element mass matrix (as formulated in local system)"""

        # Ix: "Polar moment of inertia"
        rho = self.properties['rho']
        Ix = self.properties['Iy'] + self.properties['Iz']
        A = self.properties['A']

        rx2 = Ix/A
        L = self.length
        L2 = L**2

        m_elem = np.zeros((12, 12))

        m_elem[0, 0] = 140
        m_elem[0, 6] = 70
        m_elem[1, 1] = 156
        m_elem[1, 5] = 22*L
        m_elem[1, 7] = 54
        m_elem[1, 11] = -13*L
        m_elem[2, 2] = 156
        m_elem[2, 4] = -22*L
        m_elem[2, 8] = 54
        m_elem[2, 10] = 13*L
        m_elem[3, 3] = 140*rx2
        m_elem[3, 9] = 70*rx2
        m_elem[4, 4] = 4*L2
        m_elem[4, 8] = -13*L
        m_elem[4, 10] = -3*L2
        m_elem[5, 5] = 4*L2
        m_elem[5, 7] = 13*L
        m_elem[5, 11] = -3*L2
        m_elem[6, 6] = 140
        m_elem[7, 7] = 156
        m_elem[7, 11] = -22*L
        m_elem[8, 8] = 156
        m_elem[8, 10] = 22*L
        m_elem[9, 9] = 140*rx2
        m_elem[10, 10] = 4*L2
        m_elem[11, 11] = 4*L2

        m_elem += np.triu(m_elem, k=1).T
        m_elem *= (rho*A*L)/420
        return m_elem

    def update_element_mass_matrix(self):
        """Element mass matrix (transformed to global system)"""

        # Mass matrix due to distributed element mass (density) and due to point masses
        m_elem = self.mass_matrix_local
        m_glob = self.T.T @ m_elem @ self.T
        self.mass_matrix_glob += m_glob

    def add_point_load(self, load, node_num, loc_system):
        """
        Add a point load to the element node 1 or 2

        Args:
            :load: load vector (6x1)
            :node_num: node to which loads are to be applied (1, 2)
            :loc_system: if True, loads are interpreted as being defined in the local system
        """

        load = np.array(load).reshape((6, 1))
        load_contrib = np.zeros((12, 1))

        if node_num == 1:
            load_contrib[:6, ] = load
        else:
            load_contrib[6:, ] = load

        if loc_system:
            load_contrib = self.T @ load_contrib

        self.load_vector_glob += load_contrib

    def add_distr_load(self, load, loc_system):
        """
        Add a distributed load to the element

        Args:
            :load: load vector (6x1)
            :loc_system: if True, loads are interpreted as being defined in the local system
        """

        qx, qy, qz, mx, my, mz = load
        L = self.length
        L2 = L**2

        f_d_elem = np.empty((12, 1))

        f_d_elem[0] = qx*L/2
        f_d_elem[1] = qy*L/2 - mz
        f_d_elem[2] = qz*L/2 + my
        f_d_elem[3] = mx*L/2
        f_d_elem[4] = -qz*L2/12
        f_d_elem[5] = qy*L2/12
        f_d_elem[6] = qx*L/2
        f_d_elem[7] = qy*L/2 + mz
        f_d_elem[8] = qz*L/2 - my
        f_d_elem[9] = mx*L/2
        f_d_elem[10] = qz*L2/12
        f_d_elem[11] = -qy*L2/12

        if loc_system:
            f_d_elem = self.T @ f_d_elem

        self.load_vector_glob += f_d_elem

    def add_point_mass(self, mass, node_num):
        """
        Add a point load to the element node 1 or 2

        Args:
            :mass: mass (scalar)
            :node_num: node to which mass is added (1, 2)
        """

        if node_num == 1:
            self.mass_matrix_glob[0:3, 0:3] += mass*np.identity(3)
        else:
            self.mass_matrix_glob[6:9, 6:9] += mass*np.identity(3)

    def shape_function_matrix(self, xi):
        """
        Return the shape function (basis function) matrix of shape (6, 12)

        Notes:
            * Rows 1 to 6 correspond to deformations 'ux', 'uy', 'uz',
              'tx', 'ty', 'tz' in this order

        Args:
            :xi: relative element coordinate [0, 1]

        Returns:
            :N: shape function matrix
        """

        if not (0 <= xi <= 1):
            raise ValueError("xi must be in range [0, 1]")

        L = self.length

        # Notes:
        # * At xi = 0: N1 = N3 = M1 = M5 = 1 (rest is 0)
        # * At xi = 1: N2 = N4 = M2 = M6 = 1 (rest is 0)

        N1 = 1 - xi
        N2 = xi
        N3 = 1 - 3*xi**2 + 2*xi**3
        N4 = 3*xi**2 - 2*xi**3
        N5 = L*(xi - 2*xi**2 + xi**3)
        N6 = L*(-xi**2 + xi**3)

        M1 = 1 - xi
        M2 = xi
        M3 = -(6/L)*(xi - xi**2)
        M4 = (6/L)*(xi - xi**2)
        M5 = 1 - 4*xi + 3*xi**2
        M6 = -2*xi + 3*xi**2

        N = np.zeros((6, 12))

        N[0, 0] = N1
        N[0, 6] = N2
        N[1, 1] = N3
        N[1, 5] = N5
        N[1, 7] = N4
        N[1, 11] = N6
        N[2, 2] = N3
        N[2, 4] = -N5
        N[2, 8] = N4
        N[2, 10] = -N6
        N[3, 3] = M1
        N[3, 9] = M2
        N[4, 2] = M3
        N[4, 4] = M5
        N[4, 8] = M4
        N[4, 10] = M6
        N[5, 1] = -M3
        N[5, 5] = M5
        N[5, 7] = -M4
        N[5, 11] = M6

        return N
