import numpy as np

from ._util import enumerate_with_step
from .fem.element import Element
from ._log import logger
from ._util import pairwise


# TODO: Element --> Warning when overwriting data (first, from 'b' to 'c', then, from 'a' to 'c')
# TODO: need check that all material, cross section data is set from start to end....


def get_mesh_stats(m):
    """Count number of beams, elements, nodes and DOFs"""

    r = m.results
    r.set_feature('mesh')  # TODO: Rename to 'assembly'...?

    nbeam = m.len('beam')
    nelem = 0
    nnode = 0
    ndof = 0
    for (mbeam, rbeam) in zip(m.iter('beam'), r.iter('beam')):
        nelem_per_beam = len(rbeam.get('elements'))
        nnodes_per_beam = nelem_per_beam + 1
        ndof_per_beam = nnodes_per_beam*Element.DOF_PER_NODE

        nelem += nelem_per_beam
        nnode += nnodes_per_beam
        ndof += ndof_per_beam

    logger.info(f"Discretisation:")
    logger.info(f"--> n_beams: {nbeam:4d}")
    logger.info(f"--> n_elem:  {nelem:4d}")
    logger.info(f"--> n_node:  {nnode:4d}")
    logger.info(f"--> n_dof:   {ndof:4d}")

    r.get('mesh').set('nbeam', nbeam)
    r.get('mesh').set('nelem', nelem)
    r.get('mesh').set('nnode', nnode)
    r.get('mesh').set('ndof', ndof)


def create_system_matrices(m):
    """
    Assemble global tensors:

        * :K: global stiffness matrix
        * :M: global mass matrix
        * :F: global load vector
    """

    r = m.results

    __ndof_total = 0

    # Create a stiffness matrix for each beam
    K_per_beam = []
    M_per_beam = []
    F_per_beam = []
    for i, (mbeam, rbeam) in enumerate(zip(m.iter('beam'), r.iter('beam'))):
        blup = r.get('mesh').get('abm').beams[i]
        ndof_beam = 6*(blup.nelem + 1)
        __ndof_total += ndof_beam
        K_beam = np.zeros((ndof_beam, ndof_beam))
        M_beam = np.zeros((ndof_beam, ndof_beam))
        F_beam = np.zeros((ndof_beam, 1))

        for k, abel in enumerate_with_step(blup.elements, step=6):
            phy_elem = Element.from_abstract_element(abel)
            K_beam[k:k+12, k:k+12] += phy_elem.stiffness_matrix_glob
            M_beam[k:k+12, k:k+12] += phy_elem.mass_matrix_glob
            F_beam[k:k+12] += phy_elem.load_vector_glob

        K_per_beam.append(K_beam)
        M_per_beam.append(M_beam)
        F_per_beam.append(F_beam)

    ndof_total = __ndof_total
    K = np.zeros((ndof_total, ndof_total))
    M = np.zeros((ndof_total, ndof_total))
    F = np.zeros((ndof_total, 1))

    # Paste each beam tensor into the global tensor
    paste_range = [0, 0]
    for K_beam, M_beam, F_beam in zip(K_per_beam, M_per_beam, F_per_beam):
        rx = K_beam.shape[0]
        from_r = paste_range[1]
        to_r = from_r + rx
        paste_range = [from_r, to_r]
        K[from_r:to_r, from_r:to_r] = K_beam
        M[from_r:to_r, from_r:to_r] = M_beam
        F[from_r:to_r] += F_beam

    s = r.set_feature('system')
    s.set('matrices', {'K': K, 'M': M, 'F': F})


def create_bc_matrices(m):
    """Assemble the constraint matrix"""

    # ====================================
    # ====================================
    # ====================================
    r = m.results
    ndof = r.get('system').get('matrices')['K'].shape[0]

    # mbc = m.get('bc')
    # for fix in mbc.get('fix'):
    #     ...

    B = fix_dof(0, ndof, ['all'])
    m.results.get('system').get('matrices')['B'] = B
    # ====================================
    # ====================================
    # ====================================



def fix_dof(node_number, total_ndof, dof_constraints):
    """
    Return part of constraint matrix B for fixed degrees of freedom

    Note:
        * Only non-zero rows are returned. If, say, three dof are fixed, then
          B will have size 3xndof

    Args:
        :node_number: node_number
        :total_ndof: total number of degrees of freedom
        :dof_constraints: list with dofs to be fixed
    """

    B = np.array([])
    pos_dict = {'ux': 0, 'uy': 1, 'uz': 2, 'tx': 3, 'ty': 4, 'tz': 5}

    for constraint in dof_constraints:
        if constraint == 'all':
            B = np.zeros((6, total_ndof))
            B[0:6, 6*node_number:6*node_number+6] = np.eye(6)
            break
        else:
            pos = pos_dict[constraint]

            B_row = np.zeros((1, total_ndof))
            B_row[0, 6*node_number+pos] = 1
            B = np.vstack((B, B_row)) if B.size else B_row

    return B
