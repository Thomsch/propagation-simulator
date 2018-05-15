#!/usr/bin/env python
# -*-encoding:utf8-*-

import sys
from noise import snoise2
from numpy import ndenumerate, zeros, int8
from time import sleep
from math import floor
import operator

import simulator_map
from simulator_map import SimulatorMap

class AleaPerlin(object):
    """ Met a disposition la méthode pour générer
    une carte à l'aide de l'algorithme de perlin """

    @classmethod
    def normalize(cls, val, lower_bnd, upper_bnd=0):
        """Transforme une valeur dans un intervalle donné en valeur entre 0
        et 1.

        Exemples :
        >>> normalize(2, 0, 10)
        0.2
        >>> normalize(56.5, 54.5, 64.5)
        0.2
        >>> normalize(1000, 500, 1500)
        0.5
        >>> normalize(1000, 0, 100)
        10

        Si la borne supérieure est omise, elle est remplacée par la borne
        inférieure, et la borne inférieure sera 0.
        L'intervalle inclut les bornes.

        Arguments :
        val -- valeur à normaliser
        lower_bnd -- borne inférieure de l'intervalle source
        uppr_bnd -- borne supérieure de l'intervalle de la valeur

        """
        if upper_bnd == 0:
            lower_bnd, upper_bnd = upper_bnd, lower_bnd
        return (val - lower_bnd) / (upper_bnd - lower_bnd)

    @classmethod
    def fill_map(cls, sim_map, octaves, freq, persistence, nb_clusters, seed):
        """Met à jour l'état de la grille.

        Calcule le bruit de Perlin pour chaque position x et y dans la
        grille et selon l'unité de temps actuelle. L'unité de temps est
        un entier itérant à l'infini dans un intervalle arbitraire (ici
        0..W).

        Une fois le bruit calculé pour une position, teste si la valeur
        de cette position a changé et si c'est le cas, met à jour les
        pixels de l'image correspondants à cette position.
        """

        for index, _ in ndenumerate(sim_map.grid):
            x, y = index

            i = cls.normalize(float(x), float(sim_map.width))
            j = cls.normalize(float(y), float(sim_map.height))

            noise = snoise2(i / freq, j / freq,
                        persistence=persistence,
                        octaves=octaves, base=seed)
            id_cluster = floor(cls.normalize(noise, -1, +1) * nb_clusters)
            sim_map.grid[x][y] = int(id_cluster)