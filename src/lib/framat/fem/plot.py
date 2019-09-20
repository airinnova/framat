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
Plot
"""

import logging

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm
import numpy as np
from commonlibs.logger import truncate_filepath
from commonlibs.math.vectors import rotate_vector_around_axis, unit_vector

from framat.fem.element import GlobalSystem
import framat.fileio.utils as fu

logger = logging.getLogger(__name__)

COLOR_DEFAULT = 'grey'
COLOR_UNDEFORMED = 'blue'
COLOR_DEFORMED = 'red'
COLOR_BC = 'black'
COLOR_BC_TEXT = 'white'
COLOR_LOCAL_SYS = 'green'
COLOR_GLOBAL_SYS = 'blue'
COLOR_CONC_FORCE = 'steelblue'
COLOR_CONC_MOMENT = 'purple'
COLOR_DIST_FORCE = 'steelblue'
COLOR_DIST_MOMENT = 'purple'
COLOR_FREENODE_FORCE = 'black'
COLOR_FREENODE_MOMENT = 'grey'
COLOR_FREENODE_POINT = 'navy'
COLOR_MASS = 'maroon'
COLOR_MASS_LOAD = 'maroon'

PLOT3D_DEFAULTS = [
    ['show', True],

    ['plot_bc', False],
    ['plot_deformed', False],
    ['plot_rotations', False],

    ['plot_CG_beams', False],
    ['plot_CG_total', False],
    ['plot_accel_vector', False],
    ['plot_bc', False],
    ['plot_bc_labels', False],
    ['plot_beamline_uids', False],
    ['plot_free_node_vectors', False],
    ['plot_free_nodes', False],
    ['plot_global_axes', False],
    ['plot_inertia_load_labels', False],
    ['plot_inertia_loads', False],
    ['plot_inertia_symbols', False],
    ['plot_load_labels', False],
    ['plot_loads', False],
    ['plot_local_axes', False],
    ['plot_named_nodes', False],
    ['plot_nodes', False],
    ['plot_undeformed', True],

    ['set_amplify_displacement', 1],
    ['set_amplify_rotation', 1],
    ['set_dpi', 300],
    ['set_format', 'png'],
    ['set_fontsize', 8],
    ['set_linewidth', 1.5],
    ['set_markersize', 10],
    ['set_savefig', False],
    ['set_scale_conc_loads', 1],
    ['set_scale_conc_moments', 1],
    ['set_scale_dist_loads', 1],
    ['set_scale_free_node_force', 1],
    ['set_scale_inertia_loads', 1],
    ['set_vectorwidth', 1],
]


def plot_all(frame, plots, filestructure):
    """
    Wrapper function which creates all plot defined in 'plots'

    Args:
        :frame: frame object
        :plots: input (list with plot settings as dict)
    """

    n_plots = len(plots)

    for i, settings in enumerate(plots, start=1):
        settings['plot_number'] = i

        if settings.get('show', True) or settings.get('set_savefig', False):
            logger.info(f"Creating plot {i}/{n_plots}")

            if settings.get('matrix_plots', False):
                create_matrix_plot(frame, settings)
            else:
                create_3D_plot(frame, settings, filestructure)
        else:
            logger.info(f"Skipping plot {i}/{n_plots}")


def get_all_plot_settings(ps, frame):
    """
    Return a dictionary with all plot setting

    Args:
        :plot_settings: dict with settings
        :frame: frame object

    Returns:
        :plot_settings: completed dict (defaults added if no value provided)
    """

    for default in PLOT3D_DEFAULTS:
        setting, value = default
        ps[setting] = ps.get(setting, value)

    # Other settings
    ps['marker'] = '.' if ps['plot_nodes'] else None
    ps['frame'] = frame
    ps['D'] = frame.deformation.U

    return ps


def create_3D_plot(frame, plot_settings, filestructure):
    """
    Main plotting function

    Args:
        :frame: frame object
        :plot_settings: settings dictionary
    """

    ps = get_all_plot_settings(plot_settings, frame)

    fig = plt.figure(figsize=(10, 10))
    ax = fig.gca(projection='3d')

    x_lims = [-0.01, 0.01]
    y_lims = [-0.01, 0.01]
    z_lims = [-0.01, 0.01]

    for node in frame.finder.nodes.by_uid.values():
        x, y, z = node.coord
        if x < x_lims[0]:
            x_lims[0] = x
        elif x > x_lims[1]:
            x_lims[1] = x
        if y < y_lims[0]:
            y_lims[0] = y
        elif y > y_lims[1]:
            y_lims[1] = y
        if z < z_lims[0]:
            z_lims[0] = z
        elif z > z_lims[1]:
            z_lims[1] = z

    ax.set_xlim(*x_lims)
    ax.set_ylim(*y_lims)
    ax.set_zlim(*z_lims)
    ax.set_aspect('equal')
    set_equal_aspect_3D(ax)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    if ps['plot_global_axes']:
        origin_glob = GlobalSystem.UnitVectors.Origin
        x_glob = GlobalSystem.UnitVectors.X
        y_glob = GlobalSystem.UnitVectors.Y
        z_glob = GlobalSystem.UnitVectors.Z
        ax = _coordinate_system(ax, ps, origin_glob,
                                (x_glob, y_glob, z_glob), ('X', 'Y', 'Z'),
                                color=COLOR_GLOBAL_SYS)

    if ps['plot_local_axes']:
        for beamline in frame.beamlines:
            for element in beamline.elements:
                mid_point = element.mid_point

                if ps['plot_local_axes']:
                    axes = (element.x_elem, element.y_elem, element.z_elem)
                    axes_names = ('x', 'y', 'z')
                    scale = 0.4*element.length
                    ax = _coordinate_system(ax, ps, mid_point, axes, axes_names, COLOR_LOCAL_SYS, scale)

    if ps['plot_accel_vector']:
        ax = _accel_vector(ax, ps)

    if ps['plot_undeformed']:
        ax = _undeformed(ax, ps)

    if ps['plot_named_nodes']:
        ax = _node_uids(ax, ps)

    if ps['plot_beamline_uids']:
        ax = _beamline_uids(ax, ps)

    if ps['plot_free_nodes'] or ps['plot_free_node_vectors']:
        ax = _free_nodes(ax, ps)

    if ps['plot_bc'] or ps['plot_bc_labels']:
        ax = _boundary_conditions(ax, ps)

    if ps['plot_inertia_symbols']:
        ax = _inertia_symbols(ax, ps)

    if ps['plot_inertia_loads'] or ps['plot_inertia_load_labels']:
        ax = _inertia_loads(ax, ps)

    if ps['plot_loads']:
        ax = _loads(ax, ps)

    if ps['plot_deformed']:
        ax = _deformed(ax, ps)

    if ps['plot_CG_total'] or ps['plot_CG_beams']:
        ax = _centre_of_mass(ax, ps)

    plt.tight_layout()

    if ps['set_savefig']:
        file_format = ps['set_format']
        fname = fu.join2abs(filestructure.dirs['plots'],
                            f"plot{ps['plot_number']}_" + fu.get_date_str() + f".{file_format}")
        logger.info(f"Saving plot as file: '{truncate_filepath(fname)}'")
        plt.savefig(fname, dpi=ps['set_dpi'], format=file_format)

    if ps['show']:
        plt.show()

    plt.close('all')


def set_equal_aspect_3D(plot):
    """
    Set aspect ratio of plot correctly

    Args:
        :plot: plot
    """
    # See https://stackoverflow.com/a/19248731

    extents = np.array([getattr(plot, 'get_{}lim'.format(dim))() for dim in 'xyz'])
    sz = extents[:, 1] - extents[:, 0]
    centers = np.mean(extents, axis=1)
    maxsize = max(abs(sz))
    r = maxsize/2
    for ctr, dim in zip(centers, 'xyz'):
        getattr(plot, 'set_{}lim'.format(dim))(ctr - r, ctr + r)


def _coordinate_system(plot, ps, origin, axes, axes_names, color, scale=1):
    """
    Add a coordinate system to a plot

    Args:
        :plot: plot
        :ps: plot settings
        :origin: origin of coordinate system
        :axes: tuple with axes (x, y, z)
        :axes_names: tuple with names of the axes (e.g. ('x', 'y', 'z'))
        :scale: scalar to size the length of the axis vectors

    Returns:
        :plot: modified plot object
    """

    axes = [scale*np.array(axis) for axis in axes]
    x_axis, y_axis, z_axis = axes

    for axis, axis_name in zip(axes, axes_names):
        x, y, z = origin
        u, v, w = axis
        plot.scatter(x, y, z, color=color, linewidth=ps['set_linewidth'])
        plot.quiver(x, y, z, u, v, w, length=1, color=color, linewidth=ps['set_vectorwidth'])
        plot.text(x+u, y+v, z+w, axis_name, color=color, fontsize=ps['set_fontsize'])

    # Plot xy-plane
    p1 = np.array(origin)
    p2 = np.array(origin + y_axis)
    p3 = np.array(origin + z_axis)
    p4 = np.array(origin + y_axis + z_axis)
    points = np.array([p1, p2, p3, p4])
    xx = points[:, 0].reshape(2, 2)
    yy = points[:, 1].reshape(2, 2)
    z = points[:, 2].reshape(2, 2)
    plot.plot_surface(xx, yy, z, alpha=0.4, color=color)

    return plot


def _undeformed(plot, ps):
    """
    Add the undeformed frame geometry to a plot

    Args:
        :plot: plot
        :ps: plot settings

    Returns:
        :plot: modified plot object
    """

    frame = ps['frame']

    for beamline in frame.beamlines:
        for element in beamline.elements:

            # Plot elements
            node_points = np.array([element.node1.coord, element.node2.coord])
            x = node_points[:, 0]
            y = node_points[:, 1]
            z = node_points[:, 2]

            plot.plot(x, y, z, linewidth=ps['set_linewidth'],
                      marker=ps['marker'], markersize=ps['set_markersize'], color=COLOR_UNDEFORMED)

    return plot


def _deformed(plot, ps):
    """
    Add the deformed frame geometry to a plot

    Args:
        :plot: plot
        :ps: plot settings

    Returns:
        :plot: modified plot object
    """

    frame = ps['frame']
    D = ps['D']
    u_factor = ps['set_amplify_displacement']
    t_factor = ps['set_amplify_rotation']

    i = 0
    for beamline in frame.beamlines:
        x_def = []
        y_def = []
        z_def = []

        node_y_axis = []
        theta_x = []
        theta_y = []
        theta_z = []

        for node in frame.finder.nodes.by_beamline_uid[beamline.uid]:
            x, y, z = node.coord

            x_def.append(x + u_factor*D[6*i, 0])
            y_def.append(y + u_factor*D[6*i+1, 0])
            z_def.append(z + u_factor*D[6*i+2, 0])

            if ps['plot_rotations']:
                node_y_axis.append(node.parent_element.y_elem)
                theta_x.append(t_factor*D[6*i+3, 0])
                theta_y.append(t_factor*D[6*i+4, 0])
                theta_z.append(t_factor*D[6*i+5, 0])

            i += 1

        # PLOT TRANSLATION
        plot.plot(x_def, y_def, z_def, linewidth=ps['set_linewidth'],
                  marker=ps['marker'], markersize=ps['set_markersize'], color=COLOR_DEFORMED)

        # PLOT ROTATION
        # TODO: there must be a better way
        if ps['plot_rotations']:
            j = 0
            for y_ax, tx, ty, tz in zip(node_y_axis, theta_x, theta_y, theta_z):
                # Using local y-axis to indicate rotation
                y_ax = rotate_vector_around_axis(y_ax, GlobalSystem.UnitVectors.X, tx)
                y_ax = rotate_vector_around_axis(y_ax, GlobalSystem.UnitVectors.Y, ty)
                y_ax = rotate_vector_around_axis(y_ax, GlobalSystem.UnitVectors.Z, tz)

                p1 = np.array([
                              x_def[j] - y_ax[0],
                              y_def[j] - y_ax[1],
                              z_def[j] - y_ax[2]])

                p2 = np.array([
                              x_def[j] + y_ax[0],
                              y_def[j] + y_ax[1],
                              z_def[j] + y_ax[2]])

                node_points = np.array([p1, p2])
                x = node_points[:, 0]
                y = node_points[:, 1]
                z = node_points[:, 2]

                plot.plot(x, y, z, marker=ps['marker'], linewidth=0.2*ps['set_linewidth'], color=COLOR_DEFORMED)
                j += 1

    # Indicate rigid connection in deformed state
    bc = frame.boundary_conditions.boundary_conditions

    if ps['plot_bc'] and 'connect' in bc:
        for connection in bc['connect']:
            node1_name = connection['node1']
            node2_name = connection['node2']
            node1_coord = frame.finder.nodes.by_uid[node1_name].coord
            node2_coord = frame.finder.nodes.by_uid[node2_name].coord
            node1_num = frame.finder.nodes.by_uid[node1_name].num
            node2_num = frame.finder.nodes.by_uid[node2_name].num
            def_node1 = D[6*node1_num:6*node1_num+3, 0]*ps['set_amplify_displacement']
            def_node2 = D[6*node2_num:6*node2_num+3, 0]*ps['set_amplify_displacement']

            node1_coord = node1_coord + def_node1
            node2_coord = node2_coord + def_node2

            node_points = np.array([node1_coord, node2_coord])
            x = node_points[:, 0]
            y = node_points[:, 1]
            z = node_points[:, 2]

            plot.plot(x, y, z, ':', linewidth=0.5*ps['set_linewidth'], color=COLOR_BC)

    return plot


def _boundary_conditions(plot, ps):
    """
    Add text label indicating the imposed boundary conditions

    Args:
        :plot: plot
        :ps: plot settings

    Returns:
        :plot: modified plot object
    """

    frame = ps['frame']
    bc = frame.boundary_conditions.boundary_conditions

    if 'fix' in bc:
        for entry in bc['fix']:
            node_name, constraints = entry['node'], entry['fix']

            node = frame.finder.nodes.by_uid[node_name]
            coord = node.coord
            bc_id = frame.boundary_conditions.get_identifier(constraints)
            bc_id = f"f{bc_id}"

            if ps['plot_bc']:
                plot.scatter(*coord, marker='D', color=COLOR_BC, s=20)

            if ps['plot_bc_labels']:
                plot.text(*coord, bc_id, bbox=dict(facecolor='grey', alpha=0.9),
                          horizontalalignment='center', verticalalignment='top',
                          color=COLOR_BC_TEXT, fontsize=ps['set_fontsize'])

    if 'connect' in bc:
        for connection in bc['connect']:
            node1_name = connection['node1']
            node2_name = connection['node2']
            node1_coord = frame.finder.nodes.by_uid[node1_name].coord
            node2_coord = frame.finder.nodes.by_uid[node2_name].coord
            bc_id = frame.boundary_conditions.get_identifier(connection['fix'])
            bc_id = f"c{bc_id}"

            node_points = np.array([node1_coord, node2_coord])
            x = node_points[:, 0]
            y = node_points[:, 1]
            z = node_points[:, 2]

            if ps['plot_bc']:
                plot.plot(x, y, z, '-', linewidth=ps['set_linewidth'], color=COLOR_BC)

            if ps['plot_bc_labels']:
                mid_point = (node_points[0, :] + node_points[1, :])/2
                plot.text(*mid_point, bc_id,
                          bbox=dict(facecolor='grey', alpha=0.9),
                          horizontalalignment='center', verticalalignment='top',
                          color=COLOR_BC_TEXT, fontsize=ps['set_fontsize'])

    return plot


def _node_uids(plot, ps):
    """
    Add text label indicating nodes with UIDs

    Args:
        :plot: plot
        :ps: plot settings

    Returns:
        :plot: modified plot object
    """

    frame = ps['frame']

    for node_uid, node in frame.finder.nodes.by_uid.items():
        coord = node.coord
        plot.text(*coord, node_uid,
                  bbox=dict(facecolor='orange', alpha=0.5),
                  horizontalalignment='center', verticalalignment='bottom',
                  color=COLOR_BC, fontsize=ps['set_fontsize'])
    return plot


def _beamline_uids(plot, ps):
    """
    Add text label indicating UIDs of beamlines

    Args:
        :plot: plot
        :ps: plot settings

    Returns:
        :plot: modified plot object
    """

    frame = ps['frame']

    for beam_uid, beam in frame.finder.beamlines.by_uid.items():
        coord = beam.interpolator(0.5)
        plot.text(*coord, beam_uid,
                  bbox=dict(facecolor='navy', alpha=0.5),
                  horizontalalignment='center', verticalalignment='bottom',
                  color='white', fontsize=ps['set_fontsize'])
    return plot


def _loads(plot, ps):
    """
    Add vectors and text labels indicating externally applied loads

    Args:
        :plot: plot
        :ps: plot settings

    Returns:
        :plot: modified plot object
    """

    frame = ps['frame']

    for beamline in frame.beamlines:
        for element in beamline.elements:
            # ----- Concentrated loads -----
            f_c = element.concentrated_load_vector_glob
            x1, y1, z1 = element.node1.coord
            x2, y2, z2 = element.node2.coord

            F1 = f_c[0:3, 0]
            M1 = f_c[3:6, 0]
            F2 = f_c[6:9, 0]
            M2 = f_c[9:12, 0]

            F1_mag = np.linalg.norm(F1)
            M1_mag = np.linalg.norm(M1)
            F2_mag = np.linalg.norm(F2)
            M2_mag = np.linalg.norm(M2)

            F1 = F1*ps['set_scale_conc_loads']
            M1 = M1*ps['set_scale_conc_moments']
            F2 = F2*ps['set_scale_conc_loads']
            M2 = M2*ps['set_scale_conc_moments']

            if np.linalg.norm(F1) > 0:
                plot.scatter(x1, y1, z1, color=COLOR_CONC_FORCE, linewidth=ps['set_vectorwidth'])
                plot.quiver(x1, y1, z1, F1[0], F1[1], F1[2],
                            length=1, color=COLOR_CONC_FORCE, linewidth=ps['set_vectorwidth'])
                if ps['plot_load_labels']:
                    plot.text(x1+F1[0], y1+F1[1], z1+F1[2], f"{F1_mag:.1e} N",
                              bbox=dict(facecolor=COLOR_CONC_FORCE, alpha=0.5),
                              color='black', fontsize=ps['set_fontsize'])

            if np.linalg.norm(M1) > 0:
                plot.scatter(x1, y1, z1, color=COLOR_CONC_MOMENT, linewidth=ps['set_vectorwidth'])
                plot.quiver(x1, y1, z1, M1[0], M1[1], M1[2],
                            length=1, color=COLOR_CONC_MOMENT, linewidth=ps['set_vectorwidth'])
                if ps['plot_load_labels']:
                    plot.text(x1+M1[0], y1+M1[1], z1+M1[2], f"{M1_mag:.1e} Nm",
                              bbox=dict(facecolor=COLOR_CONC_MOMENT, alpha=0.5),
                              color='black', fontsize=ps['set_fontsize'])

            if np.linalg.norm(F2) > 0:
                plot.quiver(x2, y2, z2, F2[0], F2[1], F2[2],
                            length=1, color=COLOR_CONC_FORCE, linewidth=ps['set_vectorwidth'])
                plot.scatter(x2, y2, z2, color=COLOR_CONC_FORCE, linewidth=ps['set_vectorwidth'])
                if ps['plot_load_labels']:
                    plot.text(x2+F2[0], y2+F2[1], z2+F2[2], f"{F2_mag:.1e} N",
                              bbox=dict(facecolor=COLOR_CONC_FORCE, alpha=0.5),
                              color='black', fontsize=ps['set_fontsize'])

            if np.linalg.norm(M2) > 0:
                plot.quiver(x2, y2, z2, M2[0], M2[1], M2[2],
                            length=1, color=COLOR_CONC_MOMENT, linewidth=ps['set_vectorwidth'])
                plot.scatter(x2, y2, z2, color=COLOR_CONC_MOMENT, linewidth=ps['set_vectorwidth'])
                if ps['plot_load_labels']:
                    plot.text(x2+M2[0], y2+M2[1], z2+M2[2], f"{M2_mag:.1e} Nm",
                              bbox=dict(facecolor=COLOR_CONC_MOMENT, alpha=0.5),
                              color='black', fontsize=ps['set_fontsize'])

            # ----- Distributed loads -----
            f_d = element.distributed_load_vector_glob
            x, y, z = element.mid_point

            dist_force = f_d[0:3, 0] + f_d[6:9, 0]
            dist_moment = f_d[3:6, 0] + f_d[9:12, 0]

            dist_force_mag = np.linalg.norm(dist_force)
            dist_moment_mag = np.linalg.norm(dist_moment)

            dist_force = dist_force*ps['set_scale_dist_loads']
            dist_moment = dist_moment*ps['set_scale_dist_loads']

            if np.linalg.norm(dist_force) > 0:
                plot.scatter(x, y, z, color=COLOR_DIST_FORCE, linewidth=ps['set_vectorwidth'])
                plot.quiver(x, y, z, dist_force[0], dist_force[1], dist_force[2],
                            length=1, color=COLOR_DIST_FORCE, linewidth=2*ps['set_vectorwidth'])
                if ps['plot_load_labels']:
                    plot.text(x+dist_force[0], y+dist_force[1], z+dist_force[2],
                              f"{dist_force_mag:.1e} N",
                              bbox=dict(facecolor=COLOR_DIST_FORCE, alpha=0.5),
                              color='black', fontsize=ps['set_fontsize'])

            if np.linalg.norm(dist_moment) > 0:
                plot.scatter(x, y, z, color=COLOR_DIST_MOMENT, linewidth=ps['set_vectorwidth'])
                plot.quiver(x, y, z, dist_moment[0], dist_moment[1], dist_moment[2],
                            linewidth=2*ps['set_vectorwidth'], length=1, color=COLOR_DIST_MOMENT)
                if ps['plot_load_labels']:
                    plot.text(x+dist_moment[0], y+dist_moment[1], z+dist_moment[2],
                              f"{dist_moment_mag:.1e} N",
                              bbox=dict(facecolor=COLOR_DIST_MOMENT, alpha=0.5),
                              color='black', fontsize=ps['set_fontsize'])

    return plot


def _inertia_symbols(plot, ps):
    """
    Add symbols indication masses

    Args:
        :plot: plot
        :ps: plot settings

    Returns:
        :plot: modified plot object
    """

    frame = ps['frame']

    for beamline in frame.beamlines:
        for element in beamline.elements:
            # ----- Point masses -----
            m1 = element.point_properties['m1']
            m2 = element.point_properties['m2']

            if m1 != 0:
                coord = element.node1.coord
                plot.scatter(*coord, color=COLOR_MASS, marker='s', linewidth=ps['set_linewidth'])
                plot.text(*coord, f'{m1:.1e} kg',
                          bbox=dict(facecolor='grey', alpha=0.9),
                          horizontalalignment='left', verticalalignment='top',
                          color=COLOR_BC_TEXT, fontsize=ps['set_fontsize'])

            if m2 != 0:
                coord = element.node2.coord
                plot.scatter(*coord, color=COLOR_MASS, marker='s', linewidth=ps['set_linewidth'])
                plot.text(*coord, f'{m2:.1e} kg',
                          bbox=dict(facecolor='grey', alpha=0.9),
                          horizontalalignment='left', verticalalignment='top',
                          color=COLOR_BC_TEXT, fontsize=ps['set_fontsize'])
    return plot


def _free_nodes(plot, ps):
    """
    Add free nodes and free node loads

    Args:
        :plot: plot
        :ps: plot settings

    Returns:
        :plot: modified plot object
    """

    frame = ps['frame']

    for beamline in frame.beamlines:
        for f_node in beamline.free_nodes:
            coord = f_node['coord']
            load = f_node['load']
            closest = f_node['closest_beam_node']

            points = np.array([coord, closest.coord])
            x = points[:, 0]
            y = points[:, 1]
            z = points[:, 2]

            if ps['plot_free_nodes']:
                plot.scatter(*coord, color=COLOR_FREENODE_POINT, marker='.', linewidth=ps['set_linewidth'])
                plot.plot(x, y, z, color=COLOR_FREENODE_POINT, linewidth=0.5*ps['set_linewidth'])

            if ps['plot_free_node_vectors']:
                plot.quiver(*coord, *load[0:3], length=ps['set_scale_free_node_force'],
                            color=COLOR_FREENODE_FORCE, linewidth=0.5*ps['set_vectorwidth'])
                plot.quiver(*coord, *load[3:6], length=ps['set_scale_free_node_force'],
                            color=COLOR_FREENODE_MOMENT, linewidth=0.5*ps['set_vectorwidth'])

    return plot


def _accel_vector(plot, ps):
    """
    Add a vector indicating the direction of (gravitational) acceleration

    Args:
        :plot: plot
        :ps: plot settings

    Returns:
        :plot: modified plot object
    """

    frame = ps['frame']

    accel_direction = frame.accel_direction
    accel_magnitude = np.linalg.norm(accel_direction)
    orig = 3*GlobalSystem.UnitVectors.Z
    vector = unit_vector(accel_direction)

    plot.scatter(*orig, color=COLOR_BC, linewidth=ps['set_linewidth'])
    plot.quiver(*orig, *vector, length=1, color=COLOR_BC, linewidth=ps['set_vectorwidth'])
    plot.text(*orig, f"{accel_magnitude:.2e} m/s²", color=COLOR_BC, fontsize=ps['set_fontsize'])

    return plot


def _inertia_loads(plot, ps):
    """
    Add vectors and text labels indicating inertial loads

    Args:
        :plot: plot
        :ps: plot settings

    Returns:
        :plot: modified plot object
    """

    frame = ps['frame']
    F_accel = frame.F_accel

    for i, node in frame.finder.nodes.by_number.items():
        load = F_accel[i*6:i*6+6]

        F = load[0:3]
        M = load[3:6]
        F_mag = np.linalg.norm(F)
        M_mag = np.linalg.norm(M)
        F = F*ps['set_scale_inertia_loads']
        M = M*ps['set_scale_inertia_loads']

        if np.linalg.norm(F) > 0:
            plot.scatter(*node.coord, color=COLOR_MASS_LOAD, linewidth=ps['set_vectorwidth'])
            plot.quiver(*node.coord, *F, length=1, color=COLOR_MASS_LOAD, linewidth=2*ps['set_vectorwidth'])

            if ps['plot_inertia_load_labels']:
                plot.text(*(node.coord+F[0][:]), f"{F_mag:.1e} N",
                          bbox=dict(facecolor=COLOR_MASS_LOAD, alpha=0.5),
                          color='black', fontsize=ps['set_fontsize'])

        if np.linalg.norm(M) > 0:
            plot.scatter(*node.coord, color=COLOR_MASS_LOAD, linewidth=ps['set_vectorwidth'])
            plot.quiver(*node.coord, *M, length=1, color=COLOR_MASS_LOAD, linewidth=2*ps['set_vectorwidth'])

            if ps['plot_inertia_load_labels']:
                plot.text(*(node.coord+M[0][:]), f"{M_mag:.1e} N*m",
                          bbox=dict(facecolor=COLOR_MASS_LOAD, alpha=0.5),
                          color='black', fontsize=ps['set_fontsize'])

    return plot


def _centre_of_mass(plot, ps):
    """
    Add marker indicating the centre of mass of the entire frame of beams

    Args:
        :plot: plot
        :ps: plot settings

    Returns:
        :plot: modified plot object
    """

    frame = ps['frame']
    mass_breakdown = frame.get_mass_breakdown()

    if ps['plot_CG_total']:
        coord_CG = mass_breakdown['total_CG']
        total_mass = mass_breakdown['total_mass']

        plot.scatter(*coord_CG, color='black', marker='X', s=ps['set_markersize']*10)
        plot.text(*coord_CG, f"  CG: {total_mass:.1e} kg",
                  bbox=dict(facecolor='grey', alpha=0.5),
                  color='black', fontsize=ps['set_fontsize'])

    if ps['plot_CG_beams']:
        for beamline_uid, beamline_entry in mass_breakdown['beams'].items():
            coord_CG = beamline_entry['CG']
            total_mass = beamline_entry['mass']

            plot.scatter(*coord_CG, color='black', marker='X', s=ps['set_markersize']*10)
            plot.text(*coord_CG, f"  CG {beamline_uid}: {total_mass:.1e} kg",
                      bbox=dict(facecolor='lightgrey', alpha=0.5),
                      color='black', fontsize=ps['set_fontsize'])

    return plot


def create_matrix_plot(frame, plot_settings):
    """
    Create a matrix plot

    Args:
        :frame: frame object
        :plot_settings: dict with settings
    """

    colormap = cm.get_cmap('magma')

    matrix_name_list = plot_settings['matrix_plots']['matrices']
    for i, matrix_name in enumerate(matrix_name_list, start=1):
        try:
            matrix = getattr(frame, matrix_name)
        except AttributeError:
            raise AttributeError(f"Could not find matrix '{matrix_name}'") from None

        logger.info(f"--> Creating matrix plot {i}/{len(matrix_name_list)}")

        figure = plt.figure(figsize=(9, 9))
        axes = figure.add_subplot(111)
        axes.set_aspect('equal')
        axes.matshow(matrix, cmap=colormap)
        plt.title(f"Matrix {matrix_name}")
        plt.show()
