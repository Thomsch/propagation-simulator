#!/usr/bin/env python
# -*-coding:utf-8-*-
from simerrors import *
import loader
from loader.parser import *

from loader.entity_metaclass import *
import os
from nose.tools import *

from config import Globals

class UnitTest(object):

    user_abs_path = Globals.user_abs_path

    def setup(self):
        """ Redéfinit l'objet Globals pour l'usage des tests """

        @staticmethod
        def user_abs_path():
            return os.path.abspath(os.path.join(  "unit_test", "files", "user_data"))

        Globals.user_abs_path = user_abs_path
        Globals._simulation_name = "simulation"
        # Prépare une simulation dans le vide, afin de pouvoir récupérer les différents parsers
        self.metaclass = EntityMetaclass("Humain", ["Montagne", "Zone_Risque", "Zone_Sure"])
        self.parser_actions = self.metaclass.action_parser
        self.parser_attr = self.metaclass.attr_parser

        # Dossier contenant tous les fichiers de tests.
        self.json_dir = os.path.abspath(os.path.join( "unit_test", "files", "json_script"))

    def tear_down(self):
        Globals.user_abs_path = self.user_abs_path
