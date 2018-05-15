#!/usr/bin/env python
# -*-coding:utf-8-*-
from simerrors import *
import loader
from loader.parser import *

from loader.entity_metaclass import *
import os
from nose.tools import *
from config import Globals
from user_test import UserTest

class TestParserIdentifier(UserTest):


    def test_valid_identifier(self):
        """ Identifier valide : "foo_bar" """
        self.parser_attr._validation_identifier("foo_bar")

    @raises(InvalidIdentifierError)
    def test_too_short_identifier(self):
        """ Identifier trop court : "b" """
        self.parser_attr._validation_identifier("b")

    @raises(InvalidIdentifierError)
    def test_empty_identifier(self):
        """ Identifieur vide """
        self.parser_attr._validation_identifier(None)

    @raises(InvalidIdentifierError)
    def test_attribute_bad_type(self):
        """ Attribut en liste """
        self.parser_attr._validation_identifier({})

    @raises(InvalidIdentifierError)
    def test_private_identifier(self):
        """ Définition d'attribut privé """
        self.parser_attr._validation_identifier("__mon_attribut")

    @raises(InvalidIdentifierError)
    def test_entity_name(self):
        """ Nom d'entité en minuscule """
        self.parser_attr._validation_identifier("human", first_upper=True)

    @raises(InvalidIdentifierError)
    def test_invalid_python(self):
        """ Nom de variable invalide : "hello world" """
        self.parser_attr._validation_identifier("hello world")
