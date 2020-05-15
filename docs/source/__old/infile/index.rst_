.. _sec_input_file:

Input file
==========

The complete description of a beam structure and the analysis can be defined in a *single* JSON file. Notice that the file |std_model_filename| in section :ref:`sec_getting_started` encapsulated the geometry, boundary conditions and the applied load such a model JSON file.

|name|'s model format is quite elaborate and offers a lot of options. The format may seem quite complex. This section describes the format and available options. The basic idea is to define a complex beam structure as a collection of individual beams (also referred to as beamlines). A single beam is defined by its *geometry* and the *beam properties* (material and profile data). *Loads* can be applied to individual beams. To solve a basic static analysis the structure needs to be fixed properly in space (there cannot be any "movable" parts). The entire frame structure is fixed by constraining individual beam nodes. There can also be connections between two beams.

.. toctree::
   :maxdepth: 1
   :caption: File description

   basic_structure

.. hint::

    |name| also provides a *model generator* which is an alternative interface to create and edit models. For more information see also :ref:`sec_model_gen`.
