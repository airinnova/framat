#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random

import numpy as np
from framat.stdfun import standard_run, StdRunArgs

FILENAME_SINGLE_BEAM = 'single_beam.json'
FILENAME_TRIPLE_BEAM = 'triple_beam.json'

def import_model(filename):

    with open(filename, "r") as fp:
        model = json.load(fp)

    return model


class TestLoadMapping:
    """
    Make sure that all free node loads are mapped onto structure.

    All loads must be accounted for in the final, global load vector.
    """

    num_load_points = 100

    Fx = 1
    Fy = 1
    Fz = 1
    Mx = 0
    My = 0
    Mz = 0

    def get_free_node_load_entry(self, x, y, z):
        return {"coord": [x, y, z], "load": [self.Fx, self.Fy, self.Fz, self.Mx, self.My, self.Mz]}

    def _run_mapping_test(self, filename, beam_num=0, xyz_lims=(1,1,1)):
        model = import_model(filename)

        xlim, ylim, zlim = xyz_lims
        free_node_loads = []
        for _ in range(self.num_load_points):
            x = xyz_lims[0]*random.random()
            y = xyz_lims[1]*random.random()
            z = xyz_lims[2]*random.random()
            free_node_loads.append(self.get_free_node_load_entry(x, y, z))

        model['beamlines'][beam_num]['loads']['free_nodes'] = free_node_loads

        args = StdRunArgs()
        args.filename = filename
        results = standard_run(args, model=model)
        frame = results['frame']

        sum_Fx = np.sum(frame.F[0::6])
        sum_Fy = np.sum(frame.F[0::6])
        sum_Fz = np.sum(frame.F[2::6])

        assert sum_Fx == self.num_load_points*self.Fx
        assert sum_Fy == self.num_load_points*self.Fy
        assert sum_Fz == self.num_load_points*self.Fz

    def test_single_beam(self):
        self._run_mapping_test(FILENAME_SINGLE_BEAM)

    def test_triple_beam(self):

        # Test mapping onto each beamline
        for beam_num in range(3):
            self._run_mapping_test(FILENAME_TRIPLE_BEAM, beam_num=beam_num, xyz_lims=(1,1,3))
