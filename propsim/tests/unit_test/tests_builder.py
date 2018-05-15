#!/usr/bin/env python
# -*-coding:utf-8-*-

from simerrors import *

import builder
from builder.builder import Builder

import os
from nose.tools import *
from config import Globals
from unit_test import *

class TestBuilder(UnitTest):
    def test_get_entity_names(self):
        """ TestBuilder Récupérer les noms des entités"""

        b = Builder()
        for entityName in b._get_entity_names():
            path = os.path.join(Globals.user_abs_entity_path(entityName), "attributes.json")
            assert os.path.exists(path)
        assert Builder._get_entity_names()[0] == "Moustique", \
                "Builder._get_entity_names()[0] = {}".format(Builder._get_entity_names()[0])
        assert Builder._get_entity_names()[1] == "Humain", \
                "Builder._get_entity_names()[1] = {}".format(Builder._get_entity_names()[1])

    def test_get_terrain_names(self):
        """ Récupérer les noms des entités"""
        b = Builder()
        terrains = [str(s) for s in b._get_terrain_names()]
        assert "Montagne" in terrains
        assert "Zone_Risque" in terrains

