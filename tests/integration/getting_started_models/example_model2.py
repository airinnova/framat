# The Model object is used to set up the entire structure model, and to run a
# beam analysis
from framat import Model

# Create a new instance of the Model object
model = Model()

# ===== MATERIAL =====
# Create a material definition which can be referenced when creating beams.
# Note that you can add as many materials as you want. Just provide a different
# UID (unique identifier) for each new material. Below we define the Young's
# modulus, the shear modulus and the density.
mat = model.add_feature('material', uid='dummy')
mat.set('E', 1)
mat.set('G', 1)
mat.set('rho', 1)

# ===== CROSS SECTION =====
# Besides material data, we also need cross section geometry, or more
# specifically, the cross section area, the second moments of area, and the
# torsional constant.
cs = model.add_feature('cross_section', uid='dummy')
cs.set('A', 1)
cs.set('Iy', 1)
cs.set('Iz', 1)
cs.set('J', 1)

# ===== BEAM =====
# Next, let's add a beam! We define the geometry using "named nodes", that is,
# we provide the coordinates of some "support nodes" which can be referred to
# with their UIDs.
beam = model.add_feature('beam')
beam.add('node', [0.0, 0, 0], uid='a')
beam.add('node', [1.5, 0, 0], uid='b')
beam.add('node', [1.5, 3, 0], uid='c')
beam.add('node', [0.0, 3, 0], uid='d')
# Set the number of elements for the beam.
beam.set('nelem', 40)
# Set the material, cross section and cross section orientation
beam.add('material', {'from': 'a', 'to': 'd', 'uid': 'dummy'})
beam.add('cross_section', {'from': 'a', 'to': 'd', 'uid': 'dummy'})
beam.add('orientation', {'from': 'a', 'to': 'd', 'up': [0, 0, 1]})
# Add some line loads [N/m] and point loads [N]
beam.add('distr_load', {'from': 'a', 'to': 'b', 'load': [0, 0, -2, 0, 0, 0]})
beam.add('distr_load', {'from': 'c', 'to': 'd', 'load': [0, 0, -2, 0, 0, 0]})
beam.add('distr_load', {'from': 'b', 'to': 'c', 'load': [0, 0, 1, 0, 0, 0]})
beam.add('point_load', {'at': 'b', 'load': [+0.1, +0.2, +0.3, 0, 0, 0]})
beam.add('point_load', {'at': 'c', 'load': [-0.1, -0.2, -0.3, 0, 0, 0]})

# ===== BOUNDARY CONDITIONS =====
# We also must constrain our model. Below, we fix the nodes 'a' and 'd'
bc = model.set_feature('bc')
bc.add('fix', {'node': 'a', 'fix': ['all']})
bc.add('fix', {'node': 'd', 'fix': ['all']})

# ===== POST-PROCESSING =====
# By default the analysis is run without any GUI, but to get a visual
# representation of the results we can create a plot
pp = model.set_feature('post_proc')
pp.set('plot_settings', {'show': True})
pp.add('plot', ['undeformed', 'deformed', 'node_uids', 'nodes', 'forces'])

# Run the beam analysis
results = model.run()

# ===== RESULTS =====
# The result object contains all relevant results. For instance, we may fetch
# the global load vector.
load_vector = results.get('tensors').get('F')
print(load_vector)
...
