#!/usr/bin/env python
# -*-coding:utf-8-*-

from simerrors import *


import os
from nose.tools import *
from config import Globals
from unit_test import *
import loader.anonymus_entity
from loader.anonymus_entity import new_entity_class

import os

import loader.entity
from loader.entity import Entity

from simerrors import *

import loader.anonymous_entity
from loader.anonymous_entity import new_entity_class

import loader.parser
from loader.parser.terrain_parser import TerrainParser
from loader.parser.start_parser import StartParser
from loader.parser.map_parser import MapParser

class TestBuilder(UnitTest):
    def setup(self):
        super(TestBuilder, self).setup()

        import builder
        from builder.builder import Builder
        entitynames = Builder._get_entity_names()
        terrain_names = [str(t) for t in Builder._get_terrain_names()]

        self.entity_class1 = new_entity_class(entitynames[0], terrain_names)
        self.entity_class2 = new_entity_class(entitynames[1], terrain_names)

    def test_entity_swap_immutable(self):
        """ Vérifie le swap sur des attributs immutables"""
        humain = self.entity_class1()

        humain._name = "Alfred"
        assert "Alfred" not in humain._name
        humain._swap()
        assert humain._name == "Alfred"


    @raises(InvalidIdentifierError)
    def test_entity_inexistant_property(self):
        """ Accès des attributs inexistant après génération du builder"""
        entity = self.entity_class1()
        entity.not_exists_but_anyway = 2
        print entity._frozen

    def test_entity_swap_primitive(self):
        """ Vérifie le swap sur des attributs primitif"""
        moustique = self.entity_class2()

        moustique.infected_count = 200
        assert moustique.infected_count != 200
        moustique._swap()
        assert moustique.infected_count == 200

    def test_entity_swap_mutable(self):
        """ Vérifie le swap sur des attributs mutables"""
        humain = self.entity_class1()
        humain.speed_progress.append(442)
        assert 442 not in humain.speed_progress, \
            "Les attributs de types (list) ne sont pas soumis aux swap"
        humain._swap()
        assert 442 in humain.noms_possibles


    def test_entity_id(self):
        """ Vérifie que les instances d'entités sont bien distinctes """
        humain = self.entity_class1()
        moustique1 = self.entity_class2()
        moustique2 = self.entity_class2()
        assert id(moustique1) == id(moustique1)
        assert id(moustique1) != id(moustique2)
        assert id(moustique1) != id(humain)

    def test_entity_class(self):
        """ Vérifie que deux types d'entités ont deux classes différents """
        assert self.entity_class1 != self.entity_class2
        assert id(self.entity_class1) != id(self.entity_class2)

    def test_entity_override(self):
        """ Possible de surcharger des méthodes définie comme surchargée """
        pass

    def test_entity_override_forbidden(self):
        """ La surcharge est interdite pour cette méthode """
        pass

    @raises(ScriptError)
    def test_entity_change_type(self):
        """ Impossible de changer de type des attributs """
        humain = self.entity_class2()
        humain.speed_id = "not any more an int"

    def test_entity_swap_need_refresh(self):
        """ Lors de la modification d'attributs d'attributs qui interressent le grahisme, _swap retourne True
        """
        humain = self.entity_class2()
        humain.speed_id += 2
        assert not humain._swap()

        humain._x += 2
        assert humain._swap()

    def test_entity_isolate(self):
        """Chaque instance d'attribut à bel et bien ses propres arguments swappable"""
        moustique1 = self.entity_class2()
        moustique2 = self.entity_class2()

        moustique1.speed_id = 11
        moustique2.speed_id = 12
        assert moustique1.speed_id == moustique2.speed_id

        moustique1._swap()
        moustique2._swap()
        assert moustique1.speed_id != moustique2.speed_id
