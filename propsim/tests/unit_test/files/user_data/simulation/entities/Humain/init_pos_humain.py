# -*- coding: utf8 -*-
from simutils import *

class InitPosHumain(Function):
    def __init__(self):
        pass

    @staticmethod
    def call(data, terrains_list):
        (width, height) = SimUtils.get_map_bounds()
        terrains = SimUtils.get_terrain_names()

        while True:
            x = SimUtils.random().randint(0, width - 1)
            y = SimUtils.random().randint(0, height - 1)

            if terrains[SimUtils.get_terrain_type(x, y)] in terrains_list:
                break

        # Randomisation de la direction et vitesse de base.
        data.humain.direction = [SimUtils.random().randint(-5, 5), SimUtils.random().randint(-5, 5)]
        data.humain.speed_id = SimUtils.random().randint(0, len(data.humain.speed_progress)-1)

        data.humain._move_entity(x, y)

