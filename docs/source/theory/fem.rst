FEM formulation
===============

**TODO** fix references to equations and figures

**TODO** fix alignment of multi-line equations

The governing equations **TODO** to **TODO** for the |eb| beam are conveniently solved using a FE formulation which is well suited for computational analyses. The FE discretisation can be constructed from the governing equations using the *Galerkin weighted residual method*. This section summarises the basic idea of the Galerkin method as well as the FE formulation implemented in the structure tool |name|. More detailed theoretical background on the FEM_ can be found in [Cook2002]_, [Przemieniecki1985]_, [Bathe2014]_, [Smith2014]_.

Galerkin weighted residual method
---------------------------------

In the following, the *Galerkin weighted residual method* (henceforth simply called Galerkin method) is outlined. This summary is partly based on [Cook2002]_, [Przemieniecki1985]_ where further details are given. The Galerkin method "converts" the governing differential equations into a discretised problem, eventually formulating a system of linear equations from which an approximate solution can be obtained. In general terms, a physical problem may be stated in the form

.. math::
    :label: eq_galerkin_problem_general

    D u - f = 0

where :math:`D` is a differential operator, :math:`u = u(x)` are dependent variables (e.g. displacements of a material point), :math:`x` are independent variables (e.g. coordinates of a material point) and :math:`f` is a function of :math:`x` (:math:`f` may be constant or zero). Note that the governing equations for the |eb| beam are stated in this form.

The next step in the Galerkin method is to choose an approximating solution :math:`\widetilde{u}` for :math:`u` which does not (have to) satisfy \cref{eq:galerkin_problem_general} in *every* point. Due to the approximation a residual :math:`R = R(x)` may remain. \Cref{eq:galerkin_problem_general} becomes

.. math::
    :label: eq_galerkin_problem_general_residual

    D \widetilde{u} - f = R

Typically, one chooses a polynomial for the approximating function like :math:`\widetilde{u}(x) = a_0 + a_1 \cdot x + a_2 \cdot x^2 \dots`, where the coefficients :math:`a_\text{i}` are chosen so that :math:`R` is small (in some sense). Next, one formulates a so-called *weak form*. The governing equations are no longer required to be satisfied exactly in every point but rather over the integral of a domain :math:`V`, i.e. in an average sense.

.. math::
    :label: eq_galerkin_residual_equation

    \displaystyle\int_V W_\text{i} \cdot R \,\text{d}{V} = 0 \qquad \text{for} \qquad i = 1, 2, \dots, n

The :math:`W_\text{i} = W_\text{i} (x)` are so-called weight functions. In the FEM_ formulation, the :math:`a_\text{i}` are nodal deformations which are usually the primary unknowns as shown in the following example.

Example
~~~~~~~

To illustrate the Galerkin method, the procedure will be shown for a uniform bar in axial loading (\cref{fig:bar_element}a). The equation of motion is

.. math::
    :label: eq_gov_eq_bar_element

    \frac{\partial{}}{\partial{x}} \left( E \cdot A \cdot \frac{\partial{u_x}}{\partial{x}} \right) + q_x - \varrho \cdot A \frac{\partial{}^2 u_x}{\partial{t}^2} = 0

This equation has already been stated in \cref{eq:beam_gov_eq_ux} as part of the beam equations, though without the inertia term which introduces a time dependency ($t$). \Cref{eq:gov_eq_bar_element} is also referred to as the *strong form* of the governing equations, since a solution :math:`u_x(x,t)` has to satisfy the equation in every point :math:`x` and for every point in time :math:`t`. At any arbitrary :math:`x`, the axial force in the bar is

.. math::
    :label: eq_bar_element_Fx

    F_x = A \cdot \sigma_x = E \cdot A \cdot \epsilon_x = E \cdot A \cdot \frac{\partial{}u_x}{\partial{x}}

where :math:`\sigma_x` and :math:`\epsilon_x` are the axial stress and strain, respectively.

.. _fig_bar_element:
.. figure:: ../_static/images/theory/bar_element.svg
   :width: 800 px
   :alt: Bar element
   :align: center

   **(a)** 1D bar element under distributed axial loading :math:`q_x = q_x(x)`. **(b)** Two adjacent elements from the discretised bar. After the resulting system of equations is assembled, node *b* is shared (figure adapted from [Cook2002]_ ).

With a separation of variables an approximating solution for \cref{eq:gov_eq_bar_element} of a discretised bar (\cref{fig:bar_element}b) may be formulated in the form

.. math::
    :label: eq_ux_approx

    \widetilde{u}_x(x,t) = \sum_{j=1}^n d_\text{j}(t) \cdot N_\text{j} (x)

where :math:`d_\text{j}` are unknown coefficients (here the nodal displacements), and :math:`N_\text{j}` are referred to as FEM_ *shape functions* which also serve as Galerkin weight functions. The Galerkin residual equation \eqref{eq:galerkin_residual_equation} becomes

.. math::
    :label: eq_galerkin_residual_for_bar

    \displaystyle\int_0^L N_\text{i} \cdot \left[ \sum_{j=1}^n \left( E \cdot A \cdot d_\text{j} \cdot N_\text{j}^\prime \right)' + q_x - \sum_{j=1}^n \varrho \cdot A \cdot \ddot{d}_\text{j} \cdot N_\text{j}  \right] \text{d}{x} = 0

In this case, the domain :math:`V` is the entire bar structure, i.e. the length of the bar :math:`L`. The indices :math:`i` and :math:`j` range over all shape functions (:math:`i, j = 1, 2, \dots, n`). Integrating by parts, rearranging the order of operations and substituting the force :math:`F_x` from \cref{eq:bar_element_Fx} yields

.. math::
    :label: eq_galerkin_residual_for_bar_proc2

    \sum_{j=1}^n \underbrace{ E \cdot A \displaystyle\int_0^L N'_\text{i} \cdot N'_\text{j} \,\text{d}{x} }_{K_{\text{i}\text{j}}} \cdot d_\text{j}
    - \sum_{j=1}^n \underbrace{ \varrho \cdot A \displaystyle\int_0^L N_\text{i} \cdot N_\text{j} \,\text{d}{x} }_{M_{\text{i}\text{j}}} \cdot \ddot{d}_\text{j} \nonumber \\
    = \displaystyle\int_0^L N_\text{i} \cdot q_x \,\text{d}{x} + \left[ N_\text{i} \sum_{j=1}^n F_{x,\text{j}} \right]_0^L

This equation pretty much resembles the sought-after FEM_ formulation. The highlighted terms :math:`K_{\text{i}\text{j}}` and :math:`M_{\text{i}\text{j}}` are elements of the global stiffness matrix :math:`\mathbf{K}` and mass matrix :math:`\mathbf{M}`, respectively. The summation symbolises the assembly process. The result becomes even clearer when choosing shape functions and performing the integrations. For the sake of simplicity, the bar is divided into a single element (:math:`i, j = 1, 2`). As a result of the integration by parts, the second order derivative from \cref{eq:gov_eq_bar_element} disappeared. Therefore, the approximating function :math:`\widetilde{u}_x` can be of lower order than required by the original governing equation \eqref{eq:gov_eq_bar_element}. For a bar it is sufficient to approximate the displacement field using element-wise *linear* functions.

.. math::

    \widetilde{u}_x(x,t) = \mathbf{N}(x) \cdot \mathbf{d}(t) \\
    \quad \text{with} \quad
    \mathbf{N} = \left( N_1, N_2 \right) =
    \left( 1 - \frac{x}{l_e}, \frac{x}{l_e} \right)
    \quad \text{and} \quad
    \mathbf{d} =
    \begin{pmatrix}
        u_1(t)\\
        u_2(t)
    \end{pmatrix} \nonumber

where :math:`x=0` at the left end of the element. The coefficients :math:`u_1` and :math:`u_2` have the same purpose as the :math:`a_\text{i}` mentioned above. Here, they are nodal displacements of the element (notice that :math:`N_\text{i}` is either 0 or 1 at the ends of the element, here :math:`l_e=L`). For a bar made up of a single element, \cref{eq:galerkin_residual_for_bar_proc2} becomes

.. math::
    :label: eq_bar_galerkin_almost_there

    E \cdot A \cdot \displaystyle\int_0^{L} \mathbf{B}^T \cdot \mathbf{B} \,\text{d}{x} \cdot \mathbf{d}
    - \varrho \cdot A \cdot \displaystyle\int_0^{L} \mathbf{N}^T \cdot \mathbf{N} \,\text{d}{x} \cdot \ddot{\mathbf{d}}
    = \displaystyle\int_0^{L} \mathbf{N}^T \cdot q_x \,\text{d}{x}
    + \bigl[ \mathbf{N}^T \cdot F_x \bigr]_0^{L} \\[3mm]

    \text{where} \qquad \mathbf{B} {:=} \mathbf{N}' \nonumber \\[3mm]

    \label{eq:bar_galerkin_more_like_fem}
    \underbrace{
    \frac{E \cdot A}{L} \cdot
    \begin{bmatrix}
        1  & -1 \\
        -1 &  1 \\
    \end{bmatrix}
    }_{\mathbf{K}}
    \underbrace{
    \begin{pmatrix}
        u_1 \\
        u_2 \\
    \end{pmatrix}
    }_{\mathbf{d} = \mathbf{U}}
    +
    \underbrace{
    \frac{-\varrho \cdot A \cdot L}{6} \cdot
    \begin{bmatrix}
        2 & 1 \\
        1 & 2 \\
    \end{bmatrix}
    }_{\mathbf{M}}
    \underbrace{
    \begin{pmatrix}
        \ddot{u}_1 \\
        \ddot{u}_2 \\
    \end{pmatrix}
    }_{\ddot{\mathbf{d}} = \ddot{\mathbf{U}}}
    =
    \underbrace{
    \begin{pmatrix}
        1/2 \\
        1/2
    \end{pmatrix}
    q_x
    +
    \begin{pmatrix}
        F_{x,1} \\
        F_{x,2}
    \end{pmatrix}
    }_{\mathbf{F}}

This is the well known FEM_ formulation, :math:`\mathbf{K} \cdot \mathbf{U} + \mathbf{M} \cdot \ddot{\mathbf{U}} = \mathbf{F}`. The term :math:`\mathbf{K} \cdot \mathbf{U}` represents internal elastic loads, and :math:`\mathbf{M} \cdot \ddot{\mathbf{U}}` represents the inertia loads. The right-hand side represents the external loads :math:`\mathbf{F}`. The second term in :math:`\mathbf{F}` involves the boundary conditions at the left and right end of the bar. The initial governing differential equation is now discretised and transformed into a system of equations.

In general, the discretised formulation is not equal to the exact solution but the FE formulation converges to the exact solution of the mathematical model as the mesh is refined. The rate of convergence is influenced by the choice of the shape functions. A similar procedure as shown for the bar element can be applied to derive the matrices for the *beam* which has additional |dof| for bending and torsion.

**TODO** TO BE CONTINUED

.. note::

    This summary is based on/copied from [Dettmann2019]_ with the authors permission.
