Changelog
=========

Changelog for FramAT. Version numbers try to follow `Semantic
Versioning <https://semver.org/spec/v2.0.0.html>`__.

[0.4.x] -- 2020-06-03
---------------------

Added
~~~~~

* Minor model definition update

Changed
~~~~~~~

* Improved matrix assembly

[0.4.0] -- 2020-06-02
---------------------

Added
~~~~~

* New Python API (entry point is ``from framat import Model``)

Removed
~~~~~~~

* Removed command-line interface in favour of pure Python API
* Dropped support for JSON files

[0.3.2] -- 2020-05-04
---------------------

Added
~~~~~

* Minor changes

[0.3.1] -- 2019-10-07
---------------------

Fixed
~~~~~

* Minor fix in command line tool

[0.3.0] -- 2019-09-20
---------------------

Removed
~~~~~~~

* Removed `PerimeterLine()` object and corresponding functions. "Perimeter lines" were used to interpolate deformations at some distance away from the beam axis. Reason for removal:
    * In general only marginally useful
    * Potential bug in function `get_deformation_of_point()` (`fem.beamlines`)
    * More general methods for interpolation of deformation fields now in `AeroFrame` package

[0.2.0] -- 2019-09-12
---------------------

Changed
~~~~~~~

* Changed the command line argument structure.

Removed
~~~~~~~

* Removed `framat_template` executable. Instead we only have `framat` and different *command line interface* operating modes.

[0.1.1] -- 2019-08-19
---------------------

Changed
~~~~~~~

* Updated to `commonlibs` v.0.1.1 which is incompatible with previous version.

[0.1.0] -- 2019-08-12
---------------------

* First public release of `FramAT` (Frame Analysis Tool). FramAT allows to perform general 3D Euler-Bernoulli beam analyses.

Added
~~~~~

Fixed
~~~~~
