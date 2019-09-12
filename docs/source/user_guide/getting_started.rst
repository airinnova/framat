.. _sec_getting_started:

Getting started
===============

This page briefly explains how to get started with a very simple example using |name|'s *command line interface*. Notice that a more detailed user guide can be found here: :ref:`detailed_user_guide`.

First, open a terminal and simply run the command ``framat``. A short help page should show up. |name| has different *operating modes* like ``run`` and ``example``. We can use the latter mode to create a very simple working example.

.. code::

    framat example

This will create a single JSON file called |std_model_filename| in your local working directory. This file defines a simple cantilever beam loaded with a point load at it tip. To compute the deformation run:

.. parsed-literal::

     framat run |std_model_filename_unformatted| -v

The sub-command ``run`` tells |name| to perform a FEM_ analysis, followed by the analysis definition (in this case |std_model_filename|). The additional flag ``-v`` will make |name| output additional information about the execution progress on the terminal screen. An interactive plot is created.

.. figure:: example.png
   :width: 600 px
   :alt: Example
   :align: center

   Simple cantilever beam. Undeformed and deformed beams are plotted in *blue* and *red*, respectively.

Feel free have a look at the file |std_model_filename|. You can try to change values in this file and re-run the analysis. However, don't be worried if you don't understand everything yet. More detailed instructions will be given on the following pages.

..
    .. seealso::

        Learn more about the |name|'s command line interface:

        * :ref:`command_line_interface`

        Learn more about |name|'s input files:

        * :ref:`input_files`

