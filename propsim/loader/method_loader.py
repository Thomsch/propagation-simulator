#!/usr/bin/env python
# -*-coding:utf-8-*-

from simerrors import *
import os
import imp
from config import Globals
import keyword

class MethodLoader(object):
    """ Permet le chargement dynamique de méthodes, d'après des noms de scripts définit par
    l'utilisateur """
    method_cache = {}

    @classmethod
    def __check_function_def(cls, name, param):
        if not isinstance(name, (str, unicode)):
            ex = ScriptError()
            ex.add_message("Name Given", name)
            ex.add_message("Exception Message", "Function name should be a string.")
            ex.add_message("Function Part", "Function name")
            ex.add_message("Type Excepted", "str")
            ex.add_message("Type Found", type(name).__name__)
            ex.add_message("Exception Name", "Bad Type")
            raise ex
        elif not isinstance(param, (list, tuple)):
            ex = ScriptError()
            ex.add_message("Param Given", param)
            ex.add_message("Exception Message", "Function {} parameters should be a list".format(name))
            ex.add_message("Function Part", "Function params")
            ex.add_message("Type Excepted", "str")
            ex.add_message("Type Found", type(name).__name__)
            ex.add_message("Exception Name", "Bad Type")
            raise ex

    @classmethod
    def __load_script(cls, script_name):
        """ Charge un script python dans l'environnement actuel
        le script_name doit être un chemin de fichier absolut, avec comme racine
        le dossier du domaine utilisateur.

        Gère un cache afin de ne charger qu'une fois chaque fichier dans toute
        l'exécution du logiciel. Permet de rendre le chargement des scripts par défaut et absolut
        plus rapide.
        """
        infos = os.path.splitext(script_name)
        # Convertit le chemin de fichier en chemin d'import.
        # Suppression du premier /
        import_name = infos[0].replace(os.sep, '.')
        while import_name[0] == '.':
            import_name = import_name[1:]

        if import_name in cls.method_cache:
            return cls.method_cache[import_name]

        # Conversion nom de fichier => nom de classe.
        # Règle : foo_bar.py => FooBar
        class_name = ""
        raw_class_name = infos[0].rpartition(os.sep)[2]
        for part in raw_class_name.split('_'):
            class_name += part.capitalize()

        # Importe le paquetage ou est contenu la classe.
        filename = os.path.abspath(script_name)
        # Permet de conserver des espaces de nommages corrects.
        import_name = import_name.replace(".", "_")
        try :
            # Chargement du module
            module =  imp.load_source(import_name, filename)
            # Ajout de la classe dans le scope (from <module> import <class_name>)
            action = cls.method_cache[import_name] = getattr(module, class_name)
        except IOError as e:
            ex = ScriptError()
            ex.add_message("Exception Message", e)
            ex.add_message("Import Name", import_name)
            ex.add_message("Class Name", class_name)
            ex.add_message("Script Filename", filename)
            raise ex
        return (action, class_name)

    @classmethod
    def load_trigger(cls, get_local_filename_func, trigger_name, default_trigger):
        """ Charge un trigger d'après le nom de script donné.
        Effectue des vérifications dans le cas où le trigger utilisateur
        est mal définit (hiérarchie, méthode de classes).
        """
        if trigger_name is None:
            e = ScriptError()
            e.add_message("Exception Message", "Trigger must be defined")
            raise e

        trigger_name = cls.__resolve_filename(get_local_filename_func, trigger_name+".py", default_trigger)
        (trigger, class_name) = cls.__load_script(trigger_name)
        try:
            trigger._check_trigger()     # Check la présence des méthodes importantes au trigger.
        except ParserError as e:
            e.add_message("Class Name", class_name)
            e.add_message("Trigger Filename", trigger_name)
            raise e
        return trigger

    @classmethod
    def load_function(cls, get_local_filename_func, function_description, default_function):
        """ Charge une fonction (action_performed ou is_performed), d'après
        le dictionnaire json donné. Traite les différents sucres syntaxiques
        pour la définition de fonction.
        """
        if function_description is None:
            e = ScriptError()
            e.add_message("Exception Message", "Function must be defined")
            raise e

        function_param = None
        function_name = None
        # si un nom de script contient ces caractères, il s'agit d'un
        # script pour la fonction par défaut
        mark_eval = set(',()[]+-*=?!<>;')
        # Sucre syntaxique : si la description est une chaîne de
        # caractère, nous la mettons en paramètre de la fonction par défaut
        if isinstance(function_description, (str, unicode)):
            # Sucre syntaxique pour la méthode
            function_description = [default_function, [function_description]]
        else:
            if len(function_description) <= 0:
                e = ActionMalformatedError()
                e.add_message("Exception Message", "Function is undefined")
                raise e

            function_name = function_description[0]
            # Peut être s'agit il d'une commande python => appeler un script
            # par défaut permettant de traiter les chaînes pythons fournies
            keywords = ["True", "False", "None"]
            keywords.extend(keyword.kwlist)
            if isinstance(function_name, (str, unicode)) and \
                (any((ch in mark_eval) for ch in function_name) or \
                any((word in keywords) for word in str(function_name).split(' '))):
                # Si il s'agit d'une liste de commande, nous appliquons
                # aussi aux méthodes par défaut
                function_name = default_function
                function_param = function_description

        if function_param is None and len(function_description) > 1:
            function_param = function_description[1]

        cls.__check_function_def(function_name, function_param)

        filename = cls.__resolve_filename(get_local_filename_func, function_name + '.py',
            os.sep + "default" + os.sep + "functions")
        try:
            (func, class_name) = cls.__load_script(filename)
        except ScriptError as e:
            e.add_message("Function filname", filename)
            e.add_message("Function description", function_description)
            raise e
        try:
            func._check_function()     # Vérification la présence des méthodes importantes au trigger.
        except ParserError as e:
            e.add_message("Class name", class_name)
            e.add_message("Function Filename", filename)
            raise e
        return (func, function_param)

    @classmethod
    def __resolve_filename(cls, get_local_filename_func, script_name, default_directory):
            """ Retourne le chemin absolu du script d'après son nom.
            Suit ce pseudo-code :
                Le nom du script est-il absolu ?
                ✓ Oui
                    Le script est celui définit.
                x Non
                    Le script est-il présent dans le dossier du fichier *.json ?
                    ✓ Oui
                        Le script est le script local.
                    x Non
                        Le script est un script par défaut

            En cas d'erreur, une ScriptNotFoundError est levée contenant le nom du script introuvable.
            """
            ex = ScriptNotFoundError()
            script_path = None
            if script_name.startswith("/") or script_name.startswith("\\") :
                # Nom de script absolu
                try:
                    script_path = Globals.user_abs_path() + os.sep + script_name
                    with open(script_path, "r"):
                        return os.path.abspath(script_path)
                except IOError as e:
                    # Le fichier n'existe pas, ou n'est pas disponible en lecture.
                    ex.add_message("Exception Message", e)
                    ex.add_message("Script Mode", "Absolute Script")
                    ex.add_message("Filename", script_path)
                    raise ex

            try:
                # Le script dans le dossier courant
                script_path = get_local_filename_func(script_name)
                with open(script_path, "r"):
                    return os.path.abspath(script_path)
            except IOError as e:
                ex.add_title("", "=")
                ex.add_message("Exception Message", e)
                ex.add_message("Script Filename", script_path)
                ex.add_title("Relative Script Lookup", "=")
                pass # il s'agit peut-être d'un script par défaut

            try:
                script_path = Globals.user_abs_path() + default_directory + os.sep + script_name
                with open(script_path, "r"):
                    return os.path.abspath(script_path)
            except IOError as e:
                ex.add_title("", "=")
                ex.add_message("Exception Message", e)
                ex.add_message("Script Filename", script_path)
                ex.add_title("Default Script Lookup", "=")
                raise ex

