#!/usr/bin/env python
# -*-coding:utf-8-*-

from parser import *
from simerrors import *
from loader import terrain
from loader.terrain import Terrain
from sim_parser import SimParser
import os

class TerrainParser(SimParser):
    """ Récupère les différents type des terrain depuis le fichier
    de config passé par paramètre dans la méthode read_terrains. """

    def __init__(self):
        super(TerrainParser, self).__init__("Terrain")

    def read_terrains(self, file_system_path):
        """ Lit et parse les différents types de terrain.
        Vérifie le nom des attributs pour qu'ils soient des
        identificateurs python valide.

        Arguments :
        file_system_path -- L'emplacement du fichier des terrains
        """
        path = os.path.normpath(file_system_path)
        terrains = []
        try:
            terrain_json = self._read_file(path)
            for terrain_key, terrain_attributes in terrain_json.iteritems():
                self._validation_identifier(terrain_key, False, 1)
                terrains.append(Terrain(terrain_key, terrain_attributes))
            return terrains
        except ParserError as e:
            e.add_message("Action", "Reading terrains")
            raise e