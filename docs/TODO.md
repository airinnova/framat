# TODO

## Plotting
* Add back plotting functionality
    - Constraints
* Create matrix plot (see 0.3.2)
* Compute and plot centre of mass, and mass of individual beams
* Plot inertia loads --> `F_accel`
* Plot accel vector
* Plot local axes
* Scale for deformations, vector size, ...
* Flag to chose if loads plotted in deformed or undeformed mesh

## Model definition
* Add acceleration state (define on beam level, or 'global'?) --> inertia loads
* Support for non-constant distributed properties with 'callable'
    - Loads
    - Cross section properties
    - Material properties
* Add support for "free-node" loads

## Meshing
* Element --> Warning when overwriting data (first, from 'b' to 'c', then, from 'a' to 'c')
* Need check that all material, cross section data is set from start to end....
* Check if two nodes are "too close" to each other

## Assembly
* (!!!) Add multipoint-constraints again (+ tests)
* Use sparse matrices

## Misc
* Test run multiprocessing
* Compute elastic energy

## Testing
* Loads given in local/global coordinate system

## Enhancements
* Use "Cook" notation for stiffness matrix
* Add skew bending (`E_{yz} \neq 0`)
* Analysis of free vibrations
* Time-domain analysis/Frequency-domain analysis
* Define the element/beam orientation with direction cosines as alternative option

## Boundary condition modelling
* Add option for prescribed deformations? ($b$)
* Make rigid connector more general (only restrict some dof's on each node)
* Apply boundary condition over a range of elements

## Feature ideas
* GUI
* Compute stresses
* Timoshenko beam theory
* Non-linear beam theory
* Thermal loads

## Reference axes
* Shear: Model off-centre shear axis (skew bending) --> see also COMSOL documentation
* CG: CG-axis with off-set of elastic axis
* CG: Is there a difference between a locally/globally defined point mass matrix?
* CG: Add discrete rotational moment of inertia
* CG: Apply point masses with an offset to elastic axis

## Testing
* Test all elementary cases cantilever
* Test beam mirror correct (same deformations for mirrored `Beamline()`)?
* Varying beam properties
*  Loads:
    * Point masses
    * Distributed masses
    * Gravity loads
    * "Free node" loads

## Understand
* $1/2 U^T * K * U$ equivalent to $0.5 * F * U$?
* B matrix cannot have "lines of zeros"
* Can there be multiple constraints in one node (e.g. rigid connector and fixed in 3D space)?
* Stranger things:
    - Mismatched input properties can lead to unexpected behaviour:
    - E.g. a very large cross section area 'A' may lead to "disattached" beams where should be fixed

#### ----------------------------------------------------------------------

## Documentation
* Numbers in numbered equations misaligned (on top instead of on right side)
* Large matrices don't fit on page (smaller math font? smaller matrix?)
