import numpy as np

from ._util import enumerate_with_step
from .fem.element import Element
from ._log import logger
from ._util import pairwise


# TODO: need check that all material, cross section data is set from start to end....


def mesh_stats(m):
    """
    """

    r = m.results

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


class ElementLookup(dict):

    ######## TODO --> implement from MutableMapping..... etc

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.all_points = []
        self.elements = []

    def __missing__(self, key):
        if isinstance(key, str):
            for elem in self.elements:
                if (elem.p1.uid == key) or (elem.p2.uid == key):
                    return elem
            else:
                raise KeyError(f"{key!r}")
        elif isinstance(key, tuple):
            uid1, uid2 = key
            beginning_found = False
            elements = []
            for elem in self.elements:
                if (elem.p1.uid == uid1) or beginning_found:
                    elements.append(elem)
                    beginning_found = True
                if elem.p2.uid == uid2:
                    return elements
            else:
                raise KeyError(f"{key!r}")
        else:
            raise KeyError(f"{key!r}")


def make_elements(m):
    """Make beam elements"""

    r = m.results
    for i, (mbeam, rbeam) in enumerate(zip(m.iter('beam'), r.iter('beam'))):
        logger.info(f"Creating nodes for beam {i}")

        elem_lookup = ElementLookup()
        for p1, p2 in rbeam.get('mesh')['mesh'].iter_point_pairs():
            logger.info(f"{p1}, {p2}")
            elem = Element(p1, p2, up=[0, 0, 1])
            elem_lookup.elements.append(elem)

        rbeam.set('elements', elem_lookup.elements)

        # Set element properties add loads...

        # pdef: property definition
        for ori in mbeam.get('orientation'):
            for elem in elem_lookup[(ori['from'], ori['to'])]:
                elem.set_orientation(ori['up'])

        for mat in mbeam.get('material'):
            # TODO: --> in future non-singleton !!!
            mat_dict = {}
            for p in ('E', 'G', 'rho'):
                mat_dict[p] = m.get('material').get(p)
            for elem in elem_lookup[(mat['from'], mat['to'])]:
                elem.set_props(mat_dict)

        for cs in mbeam.get('cross_section'):
            # TODO: --> in future non-singleton !!!
            cs_dict = {}
            for p in ('A', 'Iy', 'Iz', 'J'):
                cs_dict[p] = m.get('cross_section').get(p)
            for elem in elem_lookup[(cs['from'], cs['to'])]:
                elem.set_props(cs_dict)

        ######
        ###### TODO, loads... etc
        ######

def create_system_matrices(m):
    """
    Assemble global tensors:

        * Global stiffness matrix K
        * Global load vector F
    """

    r = m.results

    logger.info("Assembling global stiffness matrix...")
    logger.info("Assembling global load matrix...")

    ndof_total = 0

    # Create a stiffness matrix for each beam
    K_per_beam = []
    M_per_beam = []
    F_per_beam = []
    for i, (mbeam, rbeam) in enumerate(zip(m.iter('beam'), r.iter('beam'))):

        ndof = 6*(len(rbeam.get('elements')) + 1)
        ndof_total += ndof

        K_beam = np.zeros((ndof, ndof))
        M_beam = np.zeros((ndof, ndof))
        F_beam = np.zeros((ndof, 1))

        elements = rbeam.get('elements')
        for k, element in enumerate_with_step(elements, step=6):
            K_beam[k:k+12, k:k+12] += element.stiffness_matrix_glob
            M_beam[k:k+12, k:k+12] += element.mass_matrix_glob
            F_beam[k:k+12] += element.load_vector_glob

        K_per_beam.append(K_beam)
        M_per_beam.append(M_beam)
        F_per_beam.append(F_beam)

    K = np.zeros((ndof_total, ndof_total))
    M = np.zeros((ndof_total, ndof_total))
    F = np.zeros((ndof_total, 1))

    # Paste each beam K matrix into global K
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
    """
    TODO
    """

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

    # ====================================
    # ====================================
    # ====================================
    r = m.results
    ndof = r.get('mesh').get('ndof')
    B = fix_dof(0, ndof, ['all'])
    # ====================================
    # ====================================
    # ====================================
    m.results.get('system').get('matrices')['B'] = B
