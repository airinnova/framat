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
beam.add('node', [0.0, 0, 0], uid='a')
beam.add('node', [1.5, 0, 0], uid='b')
beam.add('node', [1.5, 3, 0], uid='c')
beam.add('node', [0.0, 3, 0], uid='d')
beam.set('nelem', 40)
beam.add('material', {'from': 'a', 'to': 'd', 'uid': 'dummy'})
beam.add('cross_section', {'from': 'a', 'to': 'd', 'uid': 'dummy'})
beam.add('orientation', {'from': 'a', 'to': 'd', 'up': [0, 0, 1]})

beam.add('distr_load', {'from': 'a', 'to': 'b', 'load': [0, 0, -2, 0, 0, 0]})
beam.add('distr_load', {'from': 'c', 'to': 'd', 'load': [0, 0, -2, 0, 0, 0]})
beam.add('distr_load', {'from': 'b', 'to': 'c', 'load': [0, 0, 1, 0, 0, 0]})
beam.add('point_load', {'at': 'b', 'load': [+0.1, +0.2, +0.3, 0, 0, 0]})
beam.add('point_load', {'at': 'c', 'load': [-0.1, -0.2, -0.3, 0, 0, 0]})

bc = model.set_feature('bc')
bc.add('fix', {'node': 'a', 'fix': ['all']})
bc.add('fix', {'node': 'd', 'fix': ['all']})

pp = model.set_feature('post_proc')
pp.set('plot_settings', {'show': True})
pp.add('plot', ['undeformed', 'deformed', 'node_uids', 'nodes', 'forces'])

model.run()
