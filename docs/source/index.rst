Welcome to |name|'s documentation!
==================================

.. image:: _static/images/logo/logo.svg
   :width: 150 px
   :alt: Logo
   :align: right

|name_bold| (|name_long|) is a FEM_ implementation of the |eb| beam theory (also known as classical or engineering beam theory). The tool was initially written for a low-fidelity aeroelasticity_ model, but |name| is a general purpose FE_ beam implementation. Most notably, |name| provides the following functionality.

* |eb| beam analyses in 3D
* Assembly of complex beam structures
* Simple to use and documented Python API
* Highly automatable model generation
* Elaborate definition of beam geometry, properties and loads
* Highly customisable plots
* Elaborate result objects post-processing

.. figure:: _static/images/main.png
   :width: 500 px
   :alt: Example
   :align: center

   Example plot

.. toctree::
   :maxdepth: 2
   :caption: User guide

   user_guide/installation
   api/model_api_general
   api/model_api
   api/result_api

.. toctree::
   :maxdepth: 2
   :caption: Theory

   theory/index
   theory/fem

.. toctree::
   :maxdepth: 2
   :caption: Links

   references
   related_projects

.. toctree::
   :maxdepth: 1
   :caption: Changelog

   CHANGELOG.md

.. toctree::
   :maxdepth: 1
   :caption: Contributing

   contribute/index

.. toctree::
   :maxdepth: 1
   :caption: Developer documentation

   dev_doc/index
   dev_doc/program_structure
   dev_doc/conventions
   dev_doc/modules_main


Licence information
-------------------

|name| was developed at `Airinnova AB`_, Stockholm.

:Author:
    |author1|

:Licence:
    |license|
