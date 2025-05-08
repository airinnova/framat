[![Latest PyPI version](https://img.shields.io/pypi/v/framat.svg?style=flat)](https://pypi.org/project/framat/)
[![Documentation Status](https://readthedocs.org/projects/framat/badge/?version=latest)](https://framat.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/badge/license-Apache%202-blue.svg)](https://github.com/airinnova/framat/blob/master/LICENSE.txt)
[![Build status](https://travis-ci.org/airinnova/framat.svg?branch=master)](https://travis-ci.org/airinnova/framat)
[![Coverage](https://codecov.io/gh/airinnova/framat/branch/master/graph/badge.svg)](https://codecov.io/gh/airinnova/framat)

---

![FramAT Logo](https://raw.githubusercontent.com/airinnova/framat/master/docs/source/_static/images/logo/logo.png)

**FramAT** (Frame Analysis Tool) is a tool for FEM beam analyses. Currently FramAT provides a full implementation of 3D Euler-Bernoulli beam theory, also known as standard engineering beam theory.

![FramAT Logo](https://raw.githubusercontent.com/airinnova/framat/master/docs/source/_static/images/main.png)

---

## Installation

```bash
pip install framat
```

To update an existing installation:

```bash
pip install --upgrade framat
```

---

## Getting started

If you have installed FramAT, you may want to have a look at the [Getting started guide](https://framat.readthedocs.io/en/latest/user_guide/getting_started.html).

---

## Example

FramAT provides a user-friendly, easy-to-read Python interface which can be integrated in complex workflows. Try it yourself. Just import the `Model` object from the FramAT library, and define your model:

```python
from framat import Model

model = Model()

mat = model.add_feature('material', uid='dummy')
mat.set('E', 1)
mat.set('G', 1)
mat.set('rho', 1)

cs = model.add_feature('cross_section', uid='dummy')
cs.set('A', 1)
cs.set('Iy', 1)
cs.set('Iz', 1)
cs.set('J', 1)

beam = model.add_feature('beam')
beam.add('node', [0, 0, 0], uid='root')
beam.add('node', [1, 0, 0], uid='corner')
beam.add('node', [1, 1, 0], uid='tip')
beam.set('nelem', 10)
beam.add('material', {'from': 'root', 'to': 'tip', 'uid': 'dummy'})
beam.add('cross_section', {'from': 'root', 'to': 'tip', 'uid': 'dummy'})
beam.add('orientation', {'from': 'root', 'to': 'tip', 'up': [0, 0, 1]})
beam.add('point_load', {'at': 'corner', 'load': [0, 0, -1, 0, 0, 0]})

bc = model.set_feature('bc')
bc.add('fix', {'node': 'root', 'fix': ['all']})

pp = model.set_feature('post_proc')
pp.add('plot', ['undeformed', 'deformed', 'nodes'])

model.run()
```

Please refer to the [documentation](https://framat.readthedocs.io/) for more information.

---

## Additional information for developers

**For developers**: Recommended packages may be installed via `requirements.txt`.

```bash
pip install -r requirements.txt
```

---

## License

**License:** Apache-2.0

---

## ⚠ Note

Starting from version `0.3.2` to `0.4.0`, the interface for *FramAT* has changed completely to a more user-friendly Python API. Please refer to the documentation for updated instructions and examples.

Older development versions can still be found under the [releases](https://github.com/airinnova/framat/releases) (not recommended). The current interface is still under development.
