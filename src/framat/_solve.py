import numpy as np


def solve(m):
    static_load_analysis(m)



def static_load_analysis(m):
    """
    Perform a static load analysis

    Returns:
        :U: global vector of nodal displacements
        :F_react: reaction loads
    """

    r = m.results
    mat = m.results.get('system').get('matrices')
    ndof = mat['K'].shape[0]

    K = mat['K']
    B = mat['B']
    F = mat['F']
    F_accel = mat['F']

    b = np.zeros((B.shape[0], 1))

    # ===== Assemble the system of equations =====
    # Number of linear constraints
    n_lr = B.shape[0]
    Z = np.zeros((n_lr, n_lr))

    A_system = np.block([
        [K, B.T],
        [B, Z]
    ])
    x_system = np.block([
        [F + F_accel],
        [b]
    ])
    solution = np.linalg.solve(A_system, x_system)

    U = solution[0:ndof]
    F_react = solution[ndof:]
    return U, F_react
