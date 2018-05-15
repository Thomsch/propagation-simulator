#!/usr/bin/env python
# -*-coding:utf-8-*-

""" Regroupe les fonctions communes à tous les types de parsing.
Permet la validation de données, l'ouverture et la lecture de fichiers
*.json.
"""

import json
import os
import re
from simerrors import *
from config import Globals

class SimParser(object):
    """ Définit des méthodes communes aux différents parser.

    Source: http://www.lifl.fr/~riquetd/parse-a-json-file-with-comments.html
    Permet d'identifier tous les commentaires d'un fichier JSON
    """
    no_comment_regex = re.compile(
        '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
        re.DOTALL | re.MULTILINE
    )

    def __init__(self, entity_name):
        super(SimParser, self).__init__()
        self.entity_name = entity_name

    def _decode_json(self, file_handler):
        """ Supprime les commentaires du fichiers et le parse le json
        en dictionnaire, qu'il retourne"""
        try:
            # Enlever les commentaires du json
            json_content = "".join(file_handler.readlines())

            match = self.no_comment_regex.search(json_content)
            while match:
                # suppression ligne par ligne
                json_content = json_content[:match.start()] + json_content[match.end():]
                match = self.no_comment_regex.search(json_content)
            return json.loads(json_content)
        except ValueError as e:
            ex = JSONMalformatedError()
            ex.add_message("Exception message", e)
            raise ex

    def _read_file(self, filename):
        """ Ouvre un fichier depuis la racine utilisateur.
        Retourne le contenu sous format de dictionnaire json """
        abs_filename = filename
        try:
            with open(abs_filename) as file_handler:
                json_data_unicode = self._decode_json(file_handler)
                json_data_str = {}
                for json_key, json_array in json_data_unicode.iteritems():
                    json_data_str[json_key.encode("utf8")] = \
                            json_array.encode("utf8") \
                            if isinstance(json_array, unicode) \
                            else json_array
                return json_data_str

        except JSONMalformatedError as e:
            e.add_message("Absolute filename", abs_filename)
            e.add_message("Relative filename", filename)
            raise e
        except IOError as e:
            ex = JSONNotFoundError()
            ex.add_message("Exception message", e)
            ex.add_message("Filename", abs_filename)
            raise ex

    def _get_entity_filename(self, filename):
        """ Donne le chemin pour un fichier situé dans le dossier de l'entité
        actuellement parsée.
        """
        return os.path.abspath(Globals.user_abs_entity_path(self.entity_name) + os.sep +  filename)

    def _validation_keys(self, key, dic, key_types, can_none = False):
        """ Vérifie l'existance cohérente d'une clé dans un dictionnaire
        donné. Permet de faire une vérification de type, nécessaire car
        nous construisons des classes d'après des scripts utilisateurs.
        """
        if key not in dic :
            ex = ScriptError()
            ex.add_message("Exception Message", "\"{}\" clause not defined".format(key))
            raise ex

        if not can_none and dic[key] is None:
            ex = ScriptError()
            ex.add_message("Exception Message", "\"{}\" clause can not be empty".format(key))
            raise ex

        if not isinstance(dic[key] , key_types):
            ex = ScriptError()
            ex.add_message("Exception Message", "Wrong type for \"{}\"".format(key))
            ex.add_message("Value found", repr(dic[key]))
            ex.add_message("Types allowed", repr(key_types))
            ex.add_message("Types found", type(dic[key]))
            raise ex


    def _validation_identifier(self, name, \
        first_upper = False, min_length = 3):
        """ Vérifie la syntaxe d'un identifier. Il
        doit être un identifier python valide, et en plus correspondre
        aux critères demandés. Lève des exception InvalidIdentifierError
        en cas d'erreur"""
        if not isinstance(name, (str, unicode)):
            ex = InvalidIdentifierError()
            ex.add_message("Exception Message",\
             "Identifier must be a string.")
            raise ex

        if len(name) <= 0:
            ex = InvalidIdentifierError()
            ex.add_message("Exception Message",\
             "Identifier can not be empty.")
            raise ex

        if len(name) < min_length:
            ex = InvalidIdentifierError()
            ex.add_message("Exception Message",\
             "Identifier too short. Minimum length required is {}"\
                .format(min_length))
            ex.add_message("Identifier", name)
            raise ex
        #
        # Test de début de chaînes
        #
        is_overriding = name[0] == '_'
        if  is_overriding and len(name) > 1 and name[1] == '_':
                ex = InvalidIdentifierError()
                ex.add_message("Exception Message",\
                 "Identifier can not be private")
                ex.add_message("Identifier", name)
                raise ex

        if first_upper and not name[0].isupper():
            ex = InvalidIdentifierError()
            ex.add_message("Exception Message",\
             "First letter must be uppercase")
            ex.add_message("Identifier", name)
            raise ex

        # Check si il s'agit d'un identifieur python
        try:
            exec("{} = None".format(name))
        except SyntaxError as e:
            ex = InvalidIdentifierError()
            ex.add_message("Exception Message", e)
            ex.add_message("Identifier", name)
            raise ex

        return is_overriding

