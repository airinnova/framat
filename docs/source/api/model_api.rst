Model
=====


This page describes the usage of the ``Model`` object. This object provides a
pure Python API, so some basic knowledge about Python is assumed.

**The model paradigm:** A ``Model`` consists one or more *features*. For
instance, an *aircraft* model might have the feature *propulsion* and the
feature *wing*. Such a feature consists of one or more *properties*. Concrete
values can be assigned to properties. So, in our example propulsion might have
the properties *thrust* and *type*, and the *wing* feature might have
properties *span* and *mount_point* (e.g. for an engine, landing gear, or some
other technical system). We may assign some values to each of these properties.
For instance, we may set thrust to :math:`50 \textrm{kN}` or the span to
:math:`20 \textrm{m}`. How do we set these values in a Python script?

.. code:: python

    model = Model()

    prop = model.set_feature('propulsion')
    prop.set('thrust', 50e3)
    prop.set('type', 'turbofan engine')

    wing = model.add_feature('wing')
    wing.set('span', 20)
    wing.add('mount_point', (4, 2, 4))
    wing.add('mount_point', (4, 6, 4))
    wing.add('mount_point', (4, 20, 4))

Notice the method ``add_feature()``. When calling this method, we create a
*instance* of the feature we want to add (here ``'propulsion'`` and ``'wing'``).
The feature instance has ``set()`` and ``add()`` methods to assign a value to
some property. The model object will check the value. That means that you must
provide a number for the property *trust*. If you try to assign, say a string
(``'50e3'``), an error will be thrown, and the model will not continue to be
built.


.. figure:: https://raw.githubusercontent.com/airinnova/model-framework/master/src/mframework/ressources/model_api_hierarchy.svg
   :alt: Model hierarchy
   :align: center

   A model object can have multiple features, and each feature can have
   multiple sub features

**Model and feature methods:** The ``Model`` object and its features provide only few
methods. The only thing to remember is that there are ``set*`` and ``add*``
methods. The ``set*`` method will always apply if there can only be one
instance, and the ``add*`` method will apply if there can be multiple
instances. For example, an aircraft can have more than one wing, hence the
``add_feature()`` method applies. To create another wing, we simply call the
method again. However, some feature may only exists once. In our dummy aircraft
model, we impose the restriction of only adding *one* propulsion feature
(\*arguably, an aircraft model could have multiple propulsion instances, but
here we assume otherwise). To highlight that the model is *singleton*, we use
the ``set_feature()`` method. Trying to use ``add_feature('propulsion')`` will
result in an error and the model will not continue to build. Property value in
a feature can be assigned with the ``add()`` and ``set()`` methods, depending
on whether the properties are singleton or not. In the example above, the wing
may have multiple mount points, but there can only be a single wing span.

+---------------+----------------------------------+---------------------------------+
|               | **Model**                        | **Feature**                     |
+---------------+----------------------------------+---------------------------------+
| Singleton     | ``set_feature('feature_name')``  | ``set('property_name', value)`` |
+---------------+----------------------------------+---------------------------------+
| Non-singleton | ``add_feature('feature_name')``  | ``add('property_name', value)`` |
+---------------+----------------------------------+---------------------------------+

===== TODO ===== Retrieve objects/values ...

+---------------+--------------------------+---------------------------+
|               | **Model**                | **Feature**               |
+---------------+--------------------------+---------------------------+
| Singleton     | ``get('feature_name')``  | ``get('property_name')``  |
+---------------+--------------------------+---------------------------+
| Non-singleton | ``iter('feature_name')`` | ``iter('property_name')`` |
+---------------+--------------------------+---------------------------+

**Running the model** The last thing you need to know is how to run the model.
Once you set up the entire, you can call the ``run()`` method. This method will
start the actual evaluation of the model.

.. code:: python

    model = Model()
    ...  # Add features and assign values here
    results = model.run()

**Results** ===== TODO =====



Feature: material
-----------------

**Description**: Material properties
**Singleton**: True

**Required**: True

Property: E [Parent feature: material]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Description**: Young's modulus

**Singleton**: True

**Required**: True

**Schema**:

* *type*: <class 'numbers.Number'>
* *>*: 0

Property: G [Parent feature: material]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Description**: Shear modulus

**Singleton**: True

**Required**: True

**Schema**:

* *type*: <class 'numbers.Number'>
* *>*: 0

Property: rho [Parent feature: material]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Description**: Density

**Singleton**: True

**Required**: True

**Schema**:

* *type*: <class 'numbers.Number'>
* *>*: 0

Feature: cross_section
----------------------

**Description**: Cross-section properties
**Singleton**: True

**Required**: False

Property: A [Parent feature: cross_section]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Description**: Area

**Singleton**: True

**Required**: True

**Schema**:

* *type*: <class 'numbers.Number'>
* *>*: 0

Property: Iy [Parent feature: cross_section]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Description**: Second moment of area about the local y-axis

**Singleton**: True

**Required**: True

**Schema**:

* *type*: <class 'numbers.Number'>
* *>*: 0

Property: Iz [Parent feature: cross_section]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Description**: Second moment of area about the local z-axis

**Singleton**: True

**Required**: True

**Schema**:

* *type*: <class 'numbers.Number'>
* *>*: 0

Property: J [Parent feature: cross_section]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Description**: Torsional constant

**Singleton**: True

**Required**: True

**Schema**:

* *type*: <class 'numbers.Number'>
* *>*: 0

Feature: beam
-------------

**Description**: Cross-section properties
**Singleton**: False

**Required**: False

Property: nelem [Parent feature: beam]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Description**: Number of beam elements

**Singleton**: True

**Required**: False

**Schema**:

* *type*: <class 'int'>
* *>*: 0

Property: node [Parent feature: beam]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Description**: Add a beam node

**Singleton**: True

**Required**: False

**Schema**:

* *$required_keys*: ['uid', 'coord']
* *uid*: {'type': <class 'str'>}
* *coord*: {'type': <class 'list'>, 'min_len': 3, 'max_len': 3, 'item_types': <class 'numbers.Number'>}

Property: accel [Parent feature: beam]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Description**: Define a translational acceleration

**Singleton**: True

**Required**: False

**Schema**:

* *$required_keys*: ['direction']
* *direction*: {'type': <class 'list'>, 'min_len': 3, 'max_len': 3, 'item_types': <class 'numbers.Number'>}
* *accel_factor*: {'type': <class 'int'>}

Property: orientation [Parent feature: beam]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Description**: Define the beam orientation

**Singleton**: True

**Required**: False

**Schema**:

* *$required_keys*: ['from', 'to', 'up']
* *from*: {'type': <class 'str'>}
* *to*: {'type': <class 'str'>}
* *up*: {'type': <class 'list'>, 'min_len': 3, 'max_len': 3, 'item_types': <class 'numbers.Number'>}

Property: material [Parent feature: beam]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Description**: Add a material

**Singleton**: True

**Required**: False

**Schema**:

* *$required_keys*: ['from', 'to', 'uid']
* *from*: {'type': <class 'str'>}
* *to*: {'type': <class 'str'>}
* *uid*: {'type': <class 'str'>}

Property: cross_section [Parent feature: beam]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Description**: Add a cross section

**Singleton**: True

**Required**: False

**Schema**:

* *$required_keys*: ['from', 'to', 'uid']
* *from*: {'type': <class 'str'>}
* *to*: {'type': <class 'str'>}
* *uid*: {'type': <class 'str'>}

Property: load [Parent feature: beam]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Description**: Add a point load

**Singleton**: True

**Required**: False

**Schema**:

* *$required_keys*: ['at', 'load']
* *at*: {'type': <class 'str'>}
* *load*: {'type': <class 'list'>, 'min_len': 6, 'max_len': 6, 'item_types': <class 'numbers.Number'>}

Feature: bc
-----------

**Description**: Cross-section properties
**Singleton**: True

**Required**: True

Property: fix [Parent feature: bc]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Description**: Fix a beam node

**Singleton**: True

**Required**: False

**Schema**:

* *$required_keys*: ['node', 'fix']
* *node*: {'type': <class 'str'>}
* *fix*: {'type': <class 'list'>, 'min_len': 1, 'max_len': 6, 'item_types': <class 'str'>}

Property: bc [Parent feature: bc]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Description**: Connect two beam nodes

**Singleton**: True

**Required**: False

**Schema**:

* *$required_keys*: ['node1', 'node2', 'fix']
* *node1*: {'type': <class 'str'>}
* *node2*: {'type': <class 'str'>}
* *fix*: {'type': <class 'list'>, 'min_len': 1, 'max_len': 6, 'item_types': <class 'str'>}

Feature: study
--------------

**Description**: Cross-section properties
**Singleton**: True

**Required**: True

Property: type [Parent feature: study]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Description**: Define a study type

**Singleton**: True

**Required**: False

**Schema**:

* *type*: <class 'str'>
* *>*: 0

Feature: post_proc
------------------

**Description**: Cross-section properties
**Singleton**: True

**Required**: True

Property: plot [Parent feature: post_proc]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Description**: Add a plot

**Singleton**: True

**Required**: False

**Schema**:

* *$required_keys*: ['args']
* *args*: {'type': <class 'list'>, 'min_len': 1, 'item_types': <class 'dict'>}

