#!/usr/bin/env python
# -*-coding:utf-8-*-

""" Lit des fichier json des actions pour les entités. Permet de parser,
de contrôler la syntaxe du fichier, de charger les différents Trigger et
Fonction dans l'environnement courant.

# Trigger
Un utilisateur définit des actions pour une entité. Une action peut
représenter par exemple un mouvement ou une opération. Une action est
liée à un type de terrain où elle effectue d'office, et à un Trigger qui
permet de définir le comportement de l'action.

Ce comportement est un comportement introspectif. C'est-à-dire que
l'entité qui effectue son action n'a accès qu'à elle-même et aux outils
de gestion de simulation.

Un Trigger est composé de deux méthodes : is_performed et
action_performed. La première permet de vérifier si l'action doit
s'effectuer, la seconde décrit l'action. Par exemple, un Humain se
déplace uniquement le jour. Le is_performed de l'action vérifiera qu'il
fait jour, et le action_performed déplacera l'Humain.

# Fonction
Un Trigger est donc composé de deux fonctions, afin de définir le
comportement d'une action. Il est cependant possible pour l'utilisateur
de définir textuellement, ou par le biais de lien vers un fichier
python, ces différentes fonctions. Nous permettons ainsi à l'utilisateur
de définir entièrement en json ses différents Trigger.

Cette fonctionnalité permet de rendre l'apprentissage de l'écriture de
script progressif. On indique en premier lieu comment définir
directement dans le fichier de configuration comment écrire des scripts,
puis apprenons comment les déporter et les réutilisés par le biais de
script python.

"""

from simerrors import *

from sim_parser import SimParser

import os
import sys

from config import *
from loader import anonymous_trigger

import traceback

from simutils import data
from simutils.data import *
from simutils import SimUtils

from loader import method_loader
from loader.method_loader import MethodLoader

class ActionParser(SimParser):
    """ Permet de lire les des fichiers JSON contenant des
    actions d'entités."""

    """ Cache des différentes actions parsées. """
    def __init__(self, entity_name, add_action_func, register_action_func):
        super(ActionParser, self).__init__(entity_name)
        # Pour ajouter une action à la classes.
        self.add_action_func = add_action_func
        # Pour enregistrer une action sous un terrain.
        self.register_action_func = register_action_func

    def read_actions(self, overrides, overrides_static = None):
        """ Lit et parse les différentes actions du fichier d'action
        définit dans le dossier de l'entité donné. Charge les différentes
        méthodes """
        actions_filename = self._get_entity_filename("actions.json")
        json_content = None
        # Ouvre et parse le fichier en json
        try:
            json_content = self._read_file(actions_filename)
        except ParserError as e:
            e.add_message("Action", "Reading actions")
            raise e
        for action_name, json_action in json_content.iteritems():
            # Traite le nom de l'action
            try:
                is_overriding = self._validation_identifier(action_name)
            except InvalidIdentifierError as e:
                e.add_message("Filename", actions_filename)
                e.add_message("Entity", self.entity_name)

            # Si la méthode veut redéfinir une méthode vérifier qu'elle
            # est autorisée
            if is_overriding and action_name not in overrides:
                ex = InvalidIdentifierError()
                ex.add_message("Exception Message", "Overriding this method is not allowed.")
                ex.add_message("Identifier", action_name)
                ex.add_message("Methods allowed", repr(overrides))
                ex.add_message("Filename", actions_filename)
                ex.add_message("Entity", self.entity_name)
                raise ex

            try:
                self.__read_user_action(action_name, json_action, is_overriding, actions_filename)
            except PropsimError as e:
                e.add_message("Filename read", actions_filename)
                e.add_message("Entity", self.entity_name)
                e.add_message("Action name", action_name)
                raise e



    def __read_user_action(self, action_name, json_action, is_overriding, json_filename = "unknow"):
        """ Lit une action définit dans un dictionnaire json.
        """
        if not is_overriding and 'with' not in json_action:
            e = InvalidIdentifierError()
            e.add_message("Exception Message", "with must be defined")
            e.add_message("Action name", action_name)
            raise e
        elif is_overriding:
            if 'with' in json_action:
                e = InvalidIdentifierError()
                e.add_message("Exception Message", "with can not be defined")
                raise e
            json_action['with'] = []
        elif json_action['with'] == '*':
            json_action['with'] = SimUtils.get_terrain_names()

        #
        # Précondition : une action doit définir une action non vide
        # et un with valide
        #
        try:
            self._validation_keys('with', json_action, (list, tuple))
            self._validation_keys('action', json_action, (str, unicode, list, tuple))
        except ScriptError as e:
            e.add_message("Action name", action_name)
            raise e

        trigger = None
        terrains = json_action['with']
        action = json_action['action']
        if action is None :
            e = ParserError()
            e.add_message("Exception Message", "action must be defined")
            raise e

        if isinstance(action, (unicode, str)):
            default_directory = os.sep + "default"
            trigger = MethodLoader.load_trigger(\
                self._get_entity_filename,\
                action,\
                default_directory)

        else: # Il s'agit d'une liste ou d'un tuple, car passé dans préconditions.
            if is_overriding: # pas de is_performed
                is_performed_description = ["is_true", ["True"]]
                action = [is_performed_description, action]
            else:
                is_performed_description = action[0]
                action_performed_description = ["default_action_performed", []]

            if len(action) > 1 :
                action_performed_description = action[1]


            try:
                (is_performed_func, is_performed_param) = \
                    MethodLoader.load_function(self._get_entity_filename,
                                               is_performed_description,
                                               "is_true")
            except ScriptError as e:
                e.add_message("Function part", "is_performed")
                e.add_message("Default call", "is_true")
                raise e

            try:
                (action_performed_func, action_performed_param) = \
                    MethodLoader.load_function(self._get_entity_filename,
                                               action_performed_description,
                                               "exec")
            except ScriptError as e:
                e.add_message("Function part", "action_performed")
                e.add_message("Default call", "exec")
                raise e

            trigger = anonymous_trigger.new_trigger(action_name,\
                is_performed_func,\
                is_performed_param,\
                action_performed_func,\
                action_performed_param)

        def launch_action(self):
            """ Lance le trigger définit par l'utilisateur. Permet de
            mettre à jour le conteneur d'information du trigger.
            """
            launch_action_data = Data()
            launch_action_data.entity1 = self
            launch_action_data.terrains = terrains
            #
            # Appelle successivement les deux fonctions, en récupérant et
            # traitant toutes les exceptions éventuelles.
            #
            try :
                is_performed = False
                try:
                    is_performed =  trigger.is_performed(launch_action_data)
                except PropsimError as e:
                    ex = ScriptError()
                    ex.add_message("Action Fonction", "is_performed")
                    for message in e.messages:
                        ex.messages.append(message)
                    raise ex
                if is_performed:
                    try:
                        return trigger.action_performed(launch_action_data)
                    except PropsimError as e:
                        ex = ScriptError()
                        ex.add_message("Action Fonction", "action_performed")
                        for message in e.messages:
                            ex.messages.append(message)
                        raise ex
            except ScriptError as ex:
                if trigger.__name__[0] != '_': # Trigger non-anonyme
                    ex.add_message("Class Name", trigger.__name__)
                ex.add_message("Action Name", action_name)
                ex.add_message("Entity Name", self.__name__)
                ex.add_message("Action Filename", json_filename)
                raise ex

        # Définition du nom de la méthode, en cas d'introspection
        launch_action.__name__ = str(action_name)
        # Ajout du nouveau trigger à la classes
        self.add_action_func(action_name, launch_action)
        # Enregistrement de la fonction pour les différents terrains
        for terrain in terrains:
            self.register_action_func(terrain, launch_action)
