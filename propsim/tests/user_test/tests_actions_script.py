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

class TestActionsScript(UserTest):
    def test_override(self):
        """ JSON possédant des actions surchargées """
        filename =  self.json_dir + os.sep + "valid_override.json"
        data = self.parser_actions._read_file(filename)
        for action_name, json_action in data.iteritems():
            self.parser_actions._ActionParser__read_user_action(action_name, json_action, action_name.startswith("_"))

    def test_bad_override(self):
        """ JSON possédant des actions surchargées comportant des erreurs """
        for i in range(5):
            filename =  self.json_dir + os.sep + "unvalid_override"+str(i+1)+".json"
            data = self.parser_actions._read_file(filename)
            for action_name, json_action in data.iteritems():
                try:
                    self.parser_actions._ActionParser__read_user_action(action_name, json_action, action_name.startswith("_"))
                    assert False
                except:
                    assert True

    def test_valid_action(self):
        """ JSON possédant des actions valides de différentes syntaxes """
        filename =  self.json_dir + os.sep + "valid_action.json"
        data = self.parser_actions._read_file(filename)
        for action_name, json_action in data.iteritems():
            self.parser_actions._ActionParser__read_user_action(action_name, json_action, action_name.startswith("_"))

    @raises(ActionMalformatedError)
    def test_missing_parameter(self):
        """ Paramètre manquant dans les actions"""
        filename =  self.json_dir + os.sep + "unvalid_action_missing_parameter.json"
        data = self.parser_actions._read_file(filename)
        for action_name, json_action in data.iteritems():
            self.parser_actions._ActionParser__read_user_action(action_name, json_action, action_name.startswith("_"))

    @raises(ScriptError)
    def test_missing_with_clause(self):
        """ Pas de with"""
        filename =  self.json_dir + os.sep + "unvalid_action_missing_with_clause.json"
        data = self.parser_actions._read_file(filename)
        for action_name, json_action in data.iteritems():
            self.parser_actions._ActionParser__read_user_action(action_name, json_action, action_name.startswith("_"))

    @raises(ScriptError)
    def test_missing_action_clause(self):
        """ Pas de action"""
        filename =  self.json_dir + os.sep + "unvalid_action_missing_action_clause.json"
        data = self.parser_actions._read_file(filename)
        for action_name, json_action in data.iteritems():
            self.parser_actions._ActionParser__read_user_action(action_name, json_action, action_name.startswith("_"))

    @raises(ScriptNotFoundError)
    def test_script_not_found(self):
        """ Le script définit n'est trouvable nulle part"""
        filename =  self.json_dir + os.sep + "unvalid_action_script_not_found.json"
        data = self.parser_actions._read_file(filename)
        for action_name, json_action in data.iteritems():
            self.parser_actions._ActionParser__read_user_action(action_name, json_action, action_name.startswith("_"))


    @raises(ScriptError)
    def test_bad_trigger_exec(self):
        """ Définission du script faux détecté à l'exécution"""
        filename =  self.json_dir + os.sep + "unvalid_action_script_not_found.json"
        data = self.parser_actions._read_file(filename)
        for action_name, json_action in data.iteritems():
            self.parser_actions._ActionParser__read_user_action(action_name, json_action, action_name.startswith("_"))

    @raises(ScriptError)
    def test_bad_trigger(self):
        """ Le trigger est mal définit """
        filename =  self.json_dir + os.sep + "unvalid_action_bad_trigger.json"
        data = self.parser_actions._read_file(filename)
        for action_name, json_action in data.iteritems():
            self.parser_actions._ActionParser__read_user_action(action_name, json_action, action_name.startswith("_"))

    def test_bad_function(self):
        """ La fonction est mal définie """
        filename =  self.json_dir + os.sep + "unvalid_action_bad_function.json"
        data = self.parser_actions._read_file(filename)
        for action_name, json_action in data.iteritems():
            try :
                self.parser_actions._ActionParser__read_user_action(action_name, json_action, action_name.startswith("_"))
                assert False
            except ScriptNotFoundError:
                assert True

