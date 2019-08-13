Getting started
===============

This page gives a very brief overview about how to get started with |name|. A more detailed user guide can be found here: :ref:`detailed_user_guide`

**Step 1: Installation**

Make sure you have installed |name| and its external dependencies correctly (see also :ref:`installation`). If |name| is has been properly installed, you should be able to run the main executable. In a terminal, type ``framat -h``. This will generate a short help page for the command line arguments. The output should look something like this:

.. include:: _help_page.txt
    :literal:

**Step 2: Run the test example**

|name| is able to generate a simple working example. In a terminal, type:

.. code-block:: bash

     framat_template

This will generate a JSON file called |std_model_filename| in the current directory. You can open this file using any text editor. The file contains the description for a simple cantilever beam analysis. You can run the analysis by typing:

.. parsed-literal::

     framat -v |std_model_filename_unformatted|

If everything is working correctly, there should be some terminal output and a plot should appear.
