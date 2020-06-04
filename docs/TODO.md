# TODO

* Test run multiprocessing

## Important issues
* Mass matrix --> get definitions correct --> "torsional constant"/"polar moment of inertia"?
* In `Element()` --> Cover case --> Some loads may be given in global system and some given in local system (currently: if some loads defined in global system and some in local system, this might not work)
* Reduce number of "upwards dependencies": "parent beam", "parent frame", ... (better for testing and code complexity)
* `Frame()`: Work break down --> make work for individual beams
* Check: Is FE bookkeeping handled correctly? (Loads/masses/etc. always applied to "primary" nodes! How prevent adding to "secondary nodes?")
* Simplify JSON input file

#### ----------------------------------------------------------------------

## Non-critical things
* Use "Cook" notation for stiffness matrix
* Plot loads per `Beamline()` (ux, uy, ...)
* Torsional constant: `J` good name?
* Add skew bending ($E_{yz} \neq 0$)
* Analysis of free vibrations
* Define the element/beam orientation with direction cosines as alternative option (check: how done in COMSOL?)
* Rename local nodes (1) and (2) to (a) and (b)? (less confusing?)

### Boundary condition modelling
* Add option for prescribed deformations? ($b$)
* Make rigid connector more general (only restrict some dof's on each node)
* Apply boundary condition over a range of elements

### JSON schema
* Add missing schema validation checks

### Improve
* Better exception messages (and also make sure code fails at early at "correct" position)

### Beamline()
* Option to choose either linear or cubic interpolation when computing new points? And/or use approach as in COMSOL? (build from "shapes": rectangles, circles, ...)
* Mirrored loads --> sensible default?
* Add check: have beam props been applied from first to last node?
* More compact: `_get_property_interpolator` and `_get_dist_load_interpolator`

#### ----------------------------------------------------------------------

## Feature ideas
* Use a "ModelGenerator" to create a frame (create `Frame()` from dictionary or class?)
* GUI
* Use a "pathlib" for handling of paths
* Compute stresses
* Timoshenko beam theory
* Non-linear beam theory
* Thermal loads

### Reference axes
* Shear: Model off-centre shear axis (skew bending) --> see also COMSOL documentation
* CG: CG-axis with off-set of elastic axis
* CG: Is there a difference between a locally/globally defined point mass matrix?
* CG: Add discrete rotational moment of inertia
* CG: Apply point masses with an offset to elastic axis

#### ----------------------------------------------------------------------

## Testing
* Add unit tests
* Test all elementary cases cantilever
* Test beam mirror correct (same deformations for mirrored `Beamline()`)?
*  Different boundary conditions
   *  Rigid connectors (1x)
   *  Fixed boundary conditions (all + a few)
* Varying beam properties
*  Loads:
    * Point masses
    * Distributed masses
    * Gravity loads
    * "Free node" loads

#### ----------------------------------------------------------------------

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
* NOTE: `tkinter` may have to be installed separately for matplotlib to work (not included in matplotlib PyPI package?)
