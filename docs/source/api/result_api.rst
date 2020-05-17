Results
=======

The method ``run()`` returns a ``Result`` object.
You can interact  with this object in the same way as the ``Model`` object
itself. The following results are available in the result object.



.. mermaid::

    graph TD
    A[Model]
    A --> F0[deformation]


Feature: deformation
--------------------

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

*Description*: Deformation

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/point.svg
   :align: left
   :alt: singleton

*Singleton*: True

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/lifebuoy.svg
   :align: left
   :alt: required

*Required*: True

Property: max
~~~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[deformation] 
    F1 --> P1[max] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

*Description*: Maximum deformation

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/point.svg
   :align: left
   :alt: singleton

*Singleton*: True

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/lifebuoy.svg
   :align: left
   :alt: required

*Required*: True

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/clipboard-check.svg
   :align: left
   :alt: schema

*Schema*:

======== ========================
**type** <class 'numbers.Number'>
 **>**              0            
======== ========================

