#!/usr/bin/env python
# -*-coding:utf-8-*-

from parser import *
from sim_parser import SimParser
import os

import config
from config.globals import Globals
from simerrors import *

class StartParser(SimParser):
    """ Lit un fichier de config terrain.json contenant les différents
    type de terrain. """

    def __init__(self):
        super(StartParser, self).__init__("Terrain")
        self.__file_name_starter = "start.json"

        """ Liste des attributs autorisés dans le fichier de config """
        self.allowed_attributes = ["launch", "seed", "map_seed", \
            "map_generation", "map_size", "iterations", "nb_iterations_before_refresh",
            "map_generation_params", "min_delay_between_refreshes", "interaction_range",
            "display_enable", "export", "export_param", "repaint_delay", "display_quantum"]

    def get_start_params(self):
        """ Lit et parse les différents types de terrain.
        Vérifie le nom des attributs pour qu'ils soient des
        dentificateur python valide."""
        path = Globals.user_abs_path() + os.path.sep + self.__file_name_starter
        try:
            start_attrs = self._read_file(path)
            for attr, value in start_attrs.iteritems():
                if attr not in self.allowed_attributes:
                    e = ParserError()
                    e.add_message("Exception Message", "Attribute not allowed")
                    e.add_message("Attribute Name", attr)
                    raise e
            return start_attrs
        except ParserError as e:
            e.add_message("Action", "Reading start attributes")
            e.add_message("Filename", path)
            raise e
