.. _sec_getting_started:

Getting started
===============

This page briefly explains how to get started with |name|. The goal is to give you a basic understanding of how |name| works, and how analyses can be set up and run. We also explain how to fetch result data which may be of interest to you. Please note that the model interface and all available model and result parameters are explained in more detail on the following pages.

Python API
----------

|name| provides a pure Python interface which allows you to set up a beam model in a simple Python script. Therefore, some some basic Python knowledge is assumed, but no advanced skills are needed.

Built-in models
---------------

|name| includes a number of built-in models which allows you to run a full beam analysis with only a few lines of code. The simplest model is a single cantilever beam loaded with a point load at the free end. First, create a Python script (or download the script from the link below) and run it with ``python example_cantilever.py``.

**Download:** `example_cantilever.py <https://raw.githubusercontent.com/airinnova/framat/master/tests/integration/getting_started_models/example_cantilever.py>`_

.. literalinclude:: ../../../tests/integration/getting_started_models/example_cantilever.py
    :language: python

When running the script from a terminal you should see a few log entries providing feedback about the program status, and an interactive plot should be created displaying the beam model.

.. figure:: ../../../tests/integration/getting_started_models/example_cantilever.png
   :width: 500 px
   :alt: Cantilever model
   :align: center

   Simple built-in cantilever model

This example is, admittedly, not the most exciting model, but it allows you to easily check that |name| has been installed correctly on your system and works. Note that you can try to run some other (perhaps more exciting) built-in models. Just replace ``'cantilever'`` with one of the following strings.

.. include:: ../builtin_models.txt

Building your own model
-----------------------

Now, let's explore a few more options to give you an overview of how to actually set up and run your *own* model. We do not go through all features that are available to you. We only show the most basic features, but if you understand the following example you will be able to easily make use of the other features which are documented on the next pages. As with the previous example we highly encourage you to try it out yourself. Just download the script and run it. Make sure to read the comments in the script and play around with the script to get a feel for how |name| works.

**Download:** `example_model2.py <https://raw.githubusercontent.com/airinnova/framat/master/tests/integration/getting_started_models/example_model2.py>`_

.. literalinclude:: ../../../tests/integration/getting_started_models/example_model2.py
    :language: python

When running the script above you should the following plot.

.. figure:: ../../../tests/integration/getting_started_models/example_model2.png
   :width: 500 px
   :alt: Example model
   :align: center

   Example model

Fetching result data
--------------------

Whenever you perform a new analysis, you will use the ``model.run()`` method. This function will always return a results object which behaves very much like the model object itself. All available result data is fully documented on the following pages.
