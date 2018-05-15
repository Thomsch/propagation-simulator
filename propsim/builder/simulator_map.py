#!/usr/bin/env python
# -*-encoding:utf8-*-

import numpy as np

class SimulatorMap(object):
    """ Représente la carte de la simulation"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = np.zeros((width, height), dtype=int)

    def get_terrain_type(self, x, y):
        """Retourne le terrain en position x, y"""
        if x < 0 or x >= self.width or y < 0 or y >= self.height :
            raise IndexError("Le point [{}, {}] n'est pas sur la carte.".format(x, y))
        else:
            return self.grid[x][y]