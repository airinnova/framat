Model
=====

Below you will find a comprehensive list of all
available features and properties. The model object has the following features:



.. mermaid::

    graph TD
    A[Model]
    A --> F0[material]
    A --> F1[cross_section]
    A --> F2[beam]
    A --> F3[bc]
    A --> F4[study]
    A --> F5[post_proc]


Feature: material
-----------------

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

The *material* feature is optional and allows to define sets of constant            material properties. When defining the properties for a specific beam            (or parts of it), you may refer to a material set using its UID. You may            define as many sets as you like.

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/point.svg
   :align: left
   :alt: singleton

*Singleton*: False

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/lifebuoy.svg
   :align: left
   :alt: required

*Required*: False

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/lifebuoy.svg
   :align: left
   :alt: required

A UID must be provided.

Property: E
~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[material] 
    F1 --> P1[E] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Young's modulus [N/m²]

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

Property: G
~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[material] 
    F1 --> P1[G] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Shear modulus [N/m²]

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

Property: rho
~~~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[material] 
    F1 --> P1[rho] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Density [kg/m³]

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

Feature: cross_section
----------------------

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

The *cross section* feature is optional and allows to define sets of constant            cross section properties. When defining the properties for a specific beam            (or parts of it), you may refer to a cross section set using its UID. You may            define as many sets as you like.

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/point.svg
   :align: left
   :alt: singleton

*Singleton*: False

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/lifebuoy.svg
   :align: left
   :alt: required

*Required*: False

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/lifebuoy.svg
   :align: left
   :alt: required

A UID must be provided.

Property: A
~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[cross_section] 
    F1 --> P1[A] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Area [m²]

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

Property: Iy
~~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[cross_section] 
    F1 --> P1[Iy] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Second moment of area about the local y-axis [m⁴]

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

Property: Iz
~~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[cross_section] 
    F1 --> P1[Iz] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Second moment of area about the local z-axis [m⁴]

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

Property: J
~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[cross_section] 
    F1 --> P1[J] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Torsional constant [m⁴]

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

Feature: beam
-------------

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

With the 'beam' feature you can add as many beams as needed for your          model. The beam geometry is defined with so-called 'named nodes'.          These are special nodes which have a UID and which together make up a          polygonal chain. In addition, you must also specify the cross section          orientation. Beam properties (material and cross-section data) has to          be defined for the entire beam length. Optionally, you can define          loads or mass properties for an individual beam.

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/point.svg
   :align: left
   :alt: singleton

*Singleton*: False

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/lifebuoy.svg
   :align: left
   :alt: required

*Required*: False

Property: node
~~~~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[beam] 
    F1 --> P1[node] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Add a named beam node, and defines its coordinates in a global          coordinate system. A beam requires at least two nodes. Note that you          must provide a UID.

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/point.svg
   :align: left
   :alt: singleton

*Singleton*: False

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/lifebuoy.svg
   :align: left
   :alt: required

*Required*: False

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/lifebuoy.svg
   :align: left
   :alt: required

A UID must be provided.

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/clipboard-check.svg
   :align: left
   :alt: schema

*Schema*:

============== ========================
   **type**         <class 'list'>     
 **min_len**              3            
 **max_len**              3            
**item_types** <class 'numbers.Number'>
============== ========================

Property: orientation
~~~~~~~~~~~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[beam] 
    F1 --> P1[orientation] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Define a constant beam cross section orientation for a section of a beam. Refer to the start           of the beam section with the key 'from' followed by a node UID,           and refer to the end of the section with the key 'to'. The key 'up' is followed by a list (vector) indicating the direction         of the local z-axis of the beam element. The 'up' vector does not have         to be a unit vector.

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

================== ============================================================================================
**$required_keys**                                     ['from', 'to', 'up']                                    
     **from**                                    {'type': <class 'str'>, '>': 0}                               
      **to**                                     {'type': <class 'str'>, '>': 0}                               
      **up**       {'type': <class 'list'>, 'min_len': 3, 'max_len': 3, 'item_types': <class 'numbers.Number'>}
================== ============================================================================================

Property: material
~~~~~~~~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[beam] 
    F1 --> P1[material] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Define a constant material for a section of a beam. Refer to the start           of the beam section with the key 'from' followed by a node UID,           and refer to the end of the section with the key 'to'. The key 'uid' must refer to a material UID defined in the 'material' feature.

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

================== ===============================
**$required_keys**      ['from', 'to', 'uid']     
     **from**      {'type': <class 'str'>, '>': 0}
      **to**       {'type': <class 'str'>, '>': 0}
     **uid**       {'type': <class 'str'>, '>': 0}
================== ===============================

Property: cross_section
~~~~~~~~~~~~~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[beam] 
    F1 --> P1[cross_section] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Define a constant cross section for a section of a beam. Refer to the start           of the beam section with the key 'from' followed by a node UID,           and refer to the end of the section with the key 'to'. The key 'uid' must refer to a cross section UID defined in the 'cross_section' feature.

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

================== ===============================
**$required_keys**      ['from', 'to', 'uid']     
     **from**      {'type': <class 'str'>, '>': 0}
      **to**       {'type': <class 'str'>, '>': 0}
     **uid**       {'type': <class 'str'>, '>': 0}
================== ===============================

Property: point_load
~~~~~~~~~~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[beam] 
    F1 --> P1[point_load] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Add a point load

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

================== ============================================================================================
**$required_keys**                                        ['at', 'load']                                       
      **at**                                     {'type': <class 'str'>, '>': 0}                               
     **load**      {'type': <class 'list'>, 'min_len': 6, 'max_len': 6, 'item_types': <class 'numbers.Number'>}
================== ============================================================================================

Property: nelem
~~~~~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[beam] 
    F1 --> P1[nelem] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Define the number of element for the beam object. The number will          apply to the whole polygonal chain. Note that the number is only          approximate, and the actual element number is determined by the          number and location of the named nodes.

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

======== =============
**type** <class 'int'>
 **>**         0      
======== =============

Feature: bc
-----------

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Boundary conditions

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/point.svg
   :align: left
   :alt: singleton

*Singleton*: True

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/lifebuoy.svg
   :align: left
   :alt: required

*Required*: True

Property: fix
~~~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[bc] 
    F1 --> P1[fix] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Fix a beam node

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

================== =================================================================================
**$required_keys**                                  ['node', 'fix']                                 
     **node**                               {'type': <class 'str'>, '>': 0}                         
     **fix**       {'type': <class 'list'>, 'min_len': 1, 'max_len': 6, 'item_types': <class 'str'>}
================== =================================================================================

Property: connect
~~~~~~~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[bc] 
    F1 --> P1[connect] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Connect two beam nodes

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

================== =================================================================================
**$required_keys**                             ['node1', 'node2', 'fix']                            
    **node1**                               {'type': <class 'str'>, '>': 0}                         
    **node2**                               {'type': <class 'str'>, '>': 0}                         
     **fix**       {'type': <class 'list'>, 'min_len': 1, 'max_len': 6, 'item_types': <class 'str'>}
================== =================================================================================

Feature: study
--------------

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Cross-section properties

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/point.svg
   :align: left
   :alt: singleton

*Singleton*: True

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/lifebuoy.svg
   :align: left
   :alt: required

*Required*: True

Property: type
~~~~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[study] 
    F1 --> P1[type] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Define a study type

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

======== =============
**type** <class 'str'>
 **>**         0      
======== =============

Feature: post_proc
------------------

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Cross-section properties

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/point.svg
   :align: left
   :alt: singleton

*Singleton*: True

.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/lifebuoy.svg
   :align: left
   :alt: required

*Required*: True

Property: plot_settings
~~~~~~~~~~~~~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[post_proc] 
    F1 --> P1[plot_settings] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

General plot settings

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

============== ==========================================
   **show**             {'type', <class 'bool'>}         
**linewidth**  {'type': <class 'numbers.Number'>, '>': 0}
**markersize** {'type': <class 'numbers.Number'>, '>': 0}
 **fontsize**       {'type': <class 'int'>, '>': 0}      
============== ==========================================

Property: plot
~~~~~~~~~~~~~~

.. mermaid::

    graph LR
    A[Model]
    A --> F1[post_proc] 
    F1 --> P1[plot] 


.. image:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/icons/notes.svg
   :align: left
   :alt: description

Add a geometry plot

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

================= ================================================
     **type**                     <class 'tuple'>                 
**allowed_items** ('deformed', 'node_uids', 'nodes', 'undeformed')
================= ================================================

