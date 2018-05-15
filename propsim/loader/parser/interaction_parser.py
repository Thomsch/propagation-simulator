#!/usr/bin/env python
# -*-coding:utf-8-*-

from action_parser import *
from simerrors import *
from loader import anonymous_trigger


from simutils import data
from simutils.data import *
from simutils import SimUtils

class InteractionParser(SimParser):
    """ Permet de lire les des fichiers JSON contenant des
    interactions d'entités."""

    interactions_keys = ["entity1", "entity2", "interaction"]

    def __init__(self, add_function_func):
        super(InteractionParser, self).__init__(None)
        """ Crée un parser d'interaction """
        self.add_function_func = add_function_func

    def _get_interaction_filename(self, filename):
        """ Donne le fichier dans le dossier contenant
        toutes les interactions. """
        return os.path.abspath(Globals.user_abs_entity_path("interactions") + os.sep +  filename)

    def read_interactions(self):
        """ Lit un par un tous les fichiers d'interactions présent dans le dossier
        d'interactions """
        for root, dirs, filenames in os.walk(Globals.user_abs_interactions_dir()):
            for filename in filenames:
                (interaction_name, ext) = os.path.splitext(filename)
                if ext == '.json':
                    self._read_interaction_file(filename, interaction_name)


    def _read_interaction_file(self, filename, interaction_name):
        """ Lit et traite un fichier d'interaction donné """
        interaction_filename = self._get_interaction_filename(filename)
        json_content = None
        # Ouvre et parse le fichier en json
        try:
            json_content = self._read_file(interaction_filename)
        except ParserError as e:
            e.add_message("Action", "Reading interaction")
            e.add_message("Filename", os.path.absinteraction_filename)
            raise e

        # Vérifie les clés pour les interactions. Doit contenir
        # uniquement certains champs.
        for key in self.interactions_keys:
            if key not in json_content:
                e = InteractionMalformatedError()
                e.add_message("Exception Message", "Key missing for interaction")
                e.add_message("Key", key)

        if len(self.interactions_keys) < len(json_content):
            e = InteractionMalformatedError()
            e.add_message("Exception Message", "Key not allowed in interaction file")
            e.add_message("Allowed keys", ", ".join(self.interactions_keys))

        try:
            # Toutes les clés du dictionnaire d'interaction sont valides.
            self.add_function_func(*self.__parse_interaction(json_content, interaction_name))
        except InteractionMalformatedError as e:
            e.add_message("Action", "Parsing inteactions")
            e.add_message("Filename", interaction_filename)

    def __parse_interaction(self, json_content, interaction_name):
        entity1 = json_content['entity1']
        entity2 = json_content['entity2']
        interaction_description = json_content['interaction']
        trigger = None

        if isinstance(interaction_description, (str, unicode)):
            # Trigger à charger
            default_directory = os.sep + "default"
            trigger = MethodLoader.load_trigger(\
                self._get_interaction_filename,\
                interaction_description,\
                default_directory)
        elif isinstance(interaction_description, (list, tuple)):
            if len(interaction_description) != 2:
                e = InteractionMalformatedError()
                e.add_message("Exception Message", "Need is_performed and action_performed functions")
                raise e

            # Deux fonctions à charger, pas de fonction par défaut
            is_performed_description = interaction_description[0]
            action_performed_description = interaction_description[1]
            try:
                (is_performed_func, is_performed_param) = \
                    MethodLoader.load_function(self._get_interaction_filename, is_performed_description, "is_true")
            except ActionMalformatedError as e:
                e.add_message("Function part", "is_performed")
                e.add_message("Default call", "is_true")
                raise e

            try:
                (action_performed_func, action_performed_param) = \
                    MethodLoader.load_function(self._get_interaction_filename, action_performed_description, "exec")
            except ActionMalformatedError as e:
                e.add_message("Function part", "action_performed")
                e.add_message("Default call", "exec")
                raise e
            trigger = anonymous_trigger.new_trigger(interaction_name,\
                is_performed_func,\
                is_performed_param,\
                action_performed_func,\
                action_performed_param)
        else:
            # Type non géré
            e = InteractionMalformatedError()
            e.add_message("Exception Message", "Bad type for interaction field")
            raise e



        def launch_interaction(entity1, entity2):
            """ Lance le trigger définit par l'utilisateur. Permet de
            mettre à jour le conteneur d'information du trigger.
            """
            launch_action_data = Data()
            launch_action_data.entity1 = entity1
            launch_action_data.entity2 = entity2
            launch_action_data.terrains = None
            #
            # Appelle successivement les deux fonctions, en récupérant et
            # traitant toutes les exceptions éventuelles.
            #
            try :
                is_performed = False
                try:
                    is_performed =  trigger.is_performed(launch_action_data)
                except ScriptError as e:
                    ex = ScriptError()
                    ex_trace = traceback.format_exc().splitlines()
                    ex.messages.extend(reversed(e.messages))
                    ex.add_message("Interaction Fonction", "is_performed")
                    raise ex
                if is_performed:
                    try:
                        return trigger.action_performed(launch_action_data)
                    except ScriptError as e:
                        ex = ScriptError()
                        ex.messages.extend(reversed(e.messages))
                        ex.add_message("Interaction Fonction", "action_performed")
                        raise ex
            except ScriptError as ex:
                if trigger.__name__[0] != '_': # Trigger non-anonyme
                    ex.add_message("Class Name", trigger.__name__)
                ex.add_message("Interaction Name", interaction_name)
                ex.add_message("Entity1 Name", entity1.__name__)
                ex.add_message("Entity2 Name", entity2.__name__)
                raise ex

        # Définition du nom de la méthode, en cas d'introspection
        launch_interaction.__name__ = str(interaction_name)
        return (entity1, entity2, launch_interaction)



