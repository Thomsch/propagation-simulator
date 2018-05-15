#!/usr/bin/env python
# -*-coding:utf-8-*-
import os
from simerrors import ConfigError

class Globals(object):
    """ Donne tous les outils nécessaires pour ce déplacer au sein
    de l'architecture de la simulation """

    """ Le nom de la simulation a lancer, définie dans les scripts utilisateurs. """
    _simulation_name = None

    """ Le nom du dossier contenant les différentes entités"""
    entity_directory = "entities"

    """ Le nom de dossier contenant les interactions, dans le dossier des entités """
    interactions_directory = "interactions"

    """ Le nom de dossier des logs """
    log_directory = "logs"

    """ Le nom de dossier des données par défaut """
    # Liens pour le déploiement
    # default_user_dir = os.path.abspath(os.path.join("propagation_simulator"))
    # user_root =  os.path.abspath(os.path.join(os.path.expanduser('~'), "propagation_simulator"))
    
    default_user_dir = os.path.join(os.path.dirname(os.path.abspath(os.path.curdir)), "user_data")
    user_root = os.path.join(os.path.expanduser('~'), "propagation_simulator", "user_data")
    
    @staticmethod
    def user_abs_path():
        """ Retourne la racine du dossier utilisateur absolue"""
        return os.path.abspath(os.path.join(os.path.expanduser('~'), "propagation_simulator", "user_data"))

    @staticmethod
    def _user_log_dir(simulation_id):
        return os.path.abspath(os.path.join(Globals.user_abs_path(), Globals.log_directory, Globals._simulation_name, simulation_id))

    @staticmethod
    def _user_log_path(simulation_id, file_name):
        """ Retourne la racine du dossier utilisateur absolue,
        crée la structure de dossier si n'existe pas """
        return Globals._user_log_dir(simulation_id) + os.sep + file_name

    @staticmethod
    def user_abs_entity_path(entity_name):
        """ Donne la racine du dossier d'entite donné, lien absolu"""
        return os.path.abspath(os.path.join(os.path.normpath(Globals.user_abs_simulation()), Globals.entity_directory,  entity_name))

    @staticmethod
    def user_abs_simulation():
        """ Donne le lien absolu vers la simulation actuellement jouée """
        if Globals._simulation_name is None :
            e = ConfigError()
            e.add_message("Exception Message", "Globals#_simulation_name cannot be none.")
            e.add_message("Message", "FATAL ERROR - Please report this error.")
            raise e
        return os.path.abspath(os.path.join(os.path.join(Globals.user_abs_path()), Globals._simulation_name))

    @staticmethod
    def user_abs_interactions_dir():
        """ Donne la racine du dossier d'entite donné, lien absolu"""
        return os.path.abspath(os.path.join(Globals.user_abs_entity_path(Globals.interactions_directory)))
