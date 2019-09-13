.. _sec_input_file_basics:

Basic structure
===============

A |name| model file is a simple text-based file, more specifically a JSON_ file. Essentially, JSON_ files are made up of *keywords* and *data fields*. Using this keyword-data structure arbitrarily complex object definitions can be generated. Notice that there is a very strict syntax. For instance, keywords must be delimited by quotation marks and brackets must always be closed. If the JSON_ syntax of any input file is invalid, |name| will not be able to import the file. Notice also that all keywords and data entries are case-sensitive (e.g. true and false must be lower-case according to the JSON_ syntax).

.. hint::

    You can also find example files in the :ref:`sec_tutorials` section.

Each |name| model has different *basic* keys which make up the structure of the JSON file.

.. code:: json

    {
        "beamlines": [],
        "materialdata": [],
        "profildata": [],
        "acceleration": {},
        "boundary_conditions": {},
        "analysis": {},
        "postproc": {}
    }

* **beamlines** The keyword *beamlines* is followed by a *list* of all individual beams descriptions.

    .. toctree::
       :maxdepth: 1

       key_beamlines

* **materialdata** Basic material properties which can be referred to from a beam definition.

    .. toctree::
       :maxdepth: 1

       key_materialdata

* **profildata** Basic profile properties which can be referred to from a beam definition.

    .. toctree::
       :maxdepth: 1

       key_profildata

* **acceleration** Definition of an accelerated state.

    .. toctree::
       :maxdepth: 1

       key_acceleration

* **boundary_conditions** Definition of single node constraints and beam connections.

    .. toctree::
       :maxdepth: 1

       key_boundary_conditions

* **analysis** The analysis to perform.

    .. toctree::
       :maxdepth: 1

       key_analysis

* **postproc** Definition of plots and files to save.

    .. toctree::
       :maxdepth: 1

       key_postproc
