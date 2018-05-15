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


class TestParserJson(UserTest):

    def test_valid_json(self):
        """ Expressions usuelles json """
        filename = self.json_dir + os.sep + "valid_json.json"
        self.parser_attr._read_file(filename)

    def test_unvalid_attributes_json(self):
        """ attribut invalide traité """
        for i in range(5):
            filename = "{}{}unvalid_attributes{}.json".format(self.json_dir, os.sep, i + 1)
            json_data = self.parser_attr._read_file(filename)
            assert_raises(ParserError, self.parser_attr._validate_attributes, json_data)