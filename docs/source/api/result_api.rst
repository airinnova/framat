Results
=======

The method ``run()`` returns a ``Result`` object.
You can interact  with this object in the same way as the ``Model`` object
itself. The following results are available in the result object.



.. mermaid::

    graph TD
    A[Model]
    A --> F0[mesh]
    A --> F1[beam]
    A --> F2[deformation]


Feature: mesh
-------------

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

*Description*: Cross-section properties

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/point.svg
   :align: left
   :alt: singleton

*Singleton*: True

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/lifebuoy.svg
   :align: left
   :alt: required

*Required*: False

Property: global_nodes
~~~~~~~~~~~~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[mesh] 
    F1 --> P1[global_nodes] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

*Description*: Nodes (global system)

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/point.svg
   :align: left
   :alt: singleton

*Singleton*: True

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/lifebuoy.svg
   :align: left
   :alt: required

*Required*: False

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/clipboard-check.svg
   :align: left
   :alt: schema

*Schema*:

========= ============================================================================================
 **eta**                               {'type': <class 'numbers.Number'>}                             
**coord** {'type': <class 'list'>, 'min_len': 3, 'max_len': 3, 'item_types': <class 'numbers.Number'>}
========= ============================================================================================

Feature: beam
-------------

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

*Description*: Cross-section properties

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/point.svg
   :align: left
   :alt: singleton

*Singleton*: False

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/lifebuoy.svg
   :align: left
   :alt: required

*Required*: False

Property: named_node
~~~~~~~~~~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[beam] 
    F1 --> P1[named_node] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

*Description*: Named nodes

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/point.svg
   :align: left
   :alt: singleton

*Singleton*: False

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/lifebuoy.svg
   :align: left
   :alt: required

*Required*: False

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/clipboard-check.svg
   :align: left
   :alt: schema

*Schema*:

======== =============
**type** <class 'str'>
 **>**         0      
======== =============

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

