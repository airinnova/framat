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

    def __init__(self, p1, p2):
        """
        Beam finite element with 6 dof per node

        TODO
        """

        # Element geometry
        self.p1 = p1
        self.p2 = p2

        # Vectors of the local coordinate system
        self.x_elem = unit_vector(self.p2.coord - self.p1.coord)
        self.y_elem = None
        self.z_elem = None

        # Element properties and loads
        # self.properties = defaultdict(lambda: None)
        # ------------------
        self.properties = defaultdict(lambda: 1)
        # ------------------
        self.distributed_loads = defaultdict(int)
        self.concentrated_loads = defaultdict(int)
        self.point_properties = defaultdict(int)

        # ----- Additional properties -----
        # Centre position of the element
        self.mid_point = (self.p1.coord + self.p2.coord)/2
        # Centre position of the element in relative xsi coordinate
        self.mid_xsi = (self.p1.rel_coord + self.p2.rel_coord)/2
        # Length of the element
        self.length = np.linalg.norm(self.p2.coord - self.p1.coord)

    @classmethod
    def from_abstract_element(cls, a):
        new = cls(a.p1, a.p2)
        new.y_elem, new.z_elem = get_local_system_from_up(new.x_elem, a.get_attr('up'))

        for prop_type in new.PROP_TYPES:
            new.properties[prop_type] = a.get_attr(prop_type)

        return new

    #################################################################
    #################################################################
    #################################################################

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

    @property
    def transformation_matrix(self):
        """Transformation matrix"""

        x_glob = GlobalSystem.X
        y_glob = GlobalSystem.Y
        z_glob = GlobalSystem.Z

        x_elem = self.x_elem
        y_elem = self.y_elem
        z_elem = self.z_elem

        lx = direction_cosine(x_elem, x_glob)
        ly = direction_cosine(y_elem, x_glob)
        lz = direction_cosine(z_elem, x_glob)

        mx = direction_cosine(x_elem, y_glob)
        my = direction_cosine(y_elem, y_glob)
        mz = direction_cosine(z_elem, y_glob)

        nx = direction_cosine(x_elem, z_glob)
        ny = direction_cosine(y_elem, z_glob)
        nz = direction_cosine(z_elem, z_glob)

        T3 = np.array([
              [lx, mx, nx],
              [ly, my, ny],
              [lz, mz, nz],
        ])

        T = np.zeros((12, 12))
        T[0:3, 0:3] = T[3:6, 3:6] = T[6:9, 6:9] = T[9:12, 9:12] = T3
        return T

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

    @property
    def point_mass_matrix_local(self):
        """Point mass matrix"""

        M_point = np.zeros((12, 12))

        m1 = self.point_properties['m1']
        m2 = self.point_properties['m2']

        # Exit early if possible...
        if m1 == 0 and m2 == 0:
            return M_point

        M_point[0:3, 0:3] = m1*np.identity(3)
        M_point[6:9, 6:9] = m2*np.identity(3)
        return M_point

    @property
    def mass_matrix_glob(self):
        """Element mass matrix (transformed to global system)"""

        # Mass matrix due to distributed element mass (density) and due to point masses
        m_elem = self.mass_matrix_local + self.point_mass_matrix_local

        T = self.transformation_matrix
        m_glob = T.T @ m_elem @ T
        return m_glob

    @property
    def stiffness_matrix_glob(self):
        """Element stiffness matrix (transformed to global system)"""

        k_elem = self.stiffness_matrix_local
        T = self.transformation_matrix
        k_glob = T.T @ k_elem @ T
        return k_glob

    @property
    def distributed_load_vector(self):
        """Distributed load vector (as formulated in local system)"""

        qx = self.distributed_loads['qx']
        qy = self.distributed_loads['qy']
        qz = self.distributed_loads['qz']
        mx = self.distributed_loads['mx']
        my = self.distributed_loads['my']
        mz = self.distributed_loads['mz']

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

        return f_d_elem

    @property
    def distributed_load_vector_glob(self):
        """Distributed load vector (transformed to global system)"""

        T = self.transformation_matrix
        f_d_elem = self.distributed_load_vector

        # if self.distributed_loads_in_loc_system:
        #     f_d_elem = T.T @ f_d_elem

        return f_d_elem

    @property
    def concentrated_load_vector(self):
        """Concentrated load vector (here independent of coordinate system)"""

        f_c_elem = np.empty((12, 1))
        for i, load_type in enumerate(self.CONC_LOAD_TYPES):
            f_c_elem[i] = self.concentrated_loads[load_type]

        return f_c_elem

    @property
    def concentrated_load_vector_glob(self):
        """Concentrated load vector (transformed to global system)"""

        T = self.transformation_matrix
        f_c_elem = self.concentrated_load_vector

        # if self.concentrated_loads_in_loc_system:
        #     f_c_elem = T.T @ f_c_elem

        return f_c_elem

    @property
    def load_vector_glob(self):
        """Element load vector (transformed to global system)"""

        f_d_elem = self.distributed_load_vector_glob
        f_c_elem = self.concentrated_load_vector_glob
        f_elem_glob = f_d_elem + f_c_elem
        return f_elem_glob

    def update_distributed_loads(self, loads, is_loc_system):
        """
        Add the distributed loads to the element

        Notes:
            * Acceptable dictionary keys see __class__.DIST_LOAD_TYPES

        Args:
            :loads: dict with distributed loads
            :is_loc_system: flag, which, if True, makes loads be treated
                according to local coordinate system
        """

        if is_loc_system not in (True, False):
            raise ValueError

        self.distributed_loads_in_loc_system = is_loc_system

        for load_type in loads.keys():
            self.distributed_loads[load_type] += loads.get(load_type, 0)

    def update_concentrated_loads(self, loads, loc_node_number, is_loc_system):
        """
        Add concentrated loads to the element

        Notes:
            * Acceptable dictionary keys see __class__.CONC_LOAD_TYPES

        Args:
            :loads: dict with concentrated loads
            :loc_node_number: node to which loads are to be applied (1, 2)
            :is_loc_system: flag, which, if True, makes loads be treated
                according to local coordinate system
        """

        if loc_node_number not in (1, 2):
            raise ValueError

        if is_loc_system not in (True, False):
            raise ValueError

        self.concentrated_loads_in_loc_system = is_loc_system

        for load_type in loads.keys():
            self.concentrated_loads[load_type + str(loc_node_number)] \
                    += float(loads.get(load_type, 0))

    def add_pointmass(self, pointmass, loc_node_number):
        """
        Add a point mass

        Args:
            :pointmass: mass in SI units
            :loc_node_number: node to which loads are to be applied (1, 2)
        """

        if loc_node_number not in (1, 2):
            raise ValueError

        mass = f'm{loc_node_number}'  # see POINT_PROPS
        self.point_properties[mass] += pointmass

    @property
    def mass(self):
        """
        Return the mass of the element
        """

        # "Cross section mass"
        rho = self.properties['rho']
        A = self.properties['A']
        L = self.length

        # Point masses
        m1 = self.point_properties[f'm1']
        m2 = self.point_properties[f'm2']

        return rho*A*L + m1 + m2


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
