from framat import Model

m = Model.example()

beam = m.add_feature('beam')
beam.add('node', {'uid': 'a', 'coord': [0, 1, 1]})
beam.add('node', {'uid': 'b', 'coord': [0, -1, 2]})
beam.add('node', {'uid': 'c', 'coord': [0, 2, 2]})
beam.add('node', {'uid': 'd', 'coord': [2, 2, 2]})
beam.set('nelem', 40)
beam.add('material', {'from': 'a', 'to': 'd', 'uid': 'dummy'})
beam.add('cross_section', {'from': 'a', 'to': 'd', 'uid': 'dummy'})
beam.add('orientation', {'from': 'a', 'to': 'd', 'up': [0, 0, 1]})
beam.add('point_load', {'at': 'b', 'load': [0, 0, -1, 0, 0, 0]})

r = m.run()
print(r.get('mesh').get('abm').nnodes)
