.. _sec_cli:

Command line interface
======================

|name| provides a command line tool which can be used to start a VLM analysis. The executable is called |name_cli|. If you simply run |name_cli| in a terminal without any arguments, a simple help page will be printed.

.. include:: _help_page.txt
    :literal:

|name| has different *operating modes*, namely ``run`` and ``example`` (in the help page referred to as positional arguments). To get more detailed help about these operating modes, type ``framat run -h`` or ``framat example -h``.

..
    .. include:: _help_page_run.txt
        :literal:

..
    .. include:: _help_page_example.txt
        :literal:

Operating mode 'example'
------------------------

The mode ``example`` can be used to create a minimalistic working example. A JSON analysis file is created. Section :ref:`sec_getting_started` demonstrates how to use this option.

Additional arguments
~~~~~~~~~~~~~~~~~~~~

* ``-o`` or ``--output`` Name of the output file (standard name is |std_model_filename|).
* ``-f`` or ``--force`` By default, |name| will not overwrite any existing files. Using the *force* argument, existing files will be overwritten.

Operating mode 'run'
--------------------

The mode ``run`` is used read a JSON analysis file and to perform a FEM_ analysis. The JSON file name is required as the second positional argument. To evaluate an analysis defined in |std_model_filename|, you can run:

.. parsed-literal::

     framat run |std_model_filename_unformatted|

Additional arguments
~~~~~~~~~~~~~~~~~~~~

* ``-c``, ``--clean`` Remove the results directory from a previous analysis.
* ``--clean-only`` Remove the results directory from a previous analysis and exit.
* ``-v``, ``--verbose`` Verbose mode (print execution progress information).
* ``-d``, ``--debug`` Debug mode (print additional, detailed information).
* ``-q``, ``--quiet`` Print nothing (except errors).
* ``--no-schema-check`` (*Developer option*) Skip a JSON schema validation.
* ``--no-plots`` (*Developer option*) Do not create any plots.
