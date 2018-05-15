#!/usr/bin/env python
# -*-encoding:utf8-*-

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

import params
from params import Params

import config
from config.globals import Globals

from simulator_map import SimulatorMap
from simutils import SimUtils
from simulator import sim_export
from simulator.sim_export import SimExport

from numpy import ndenumerate

class Builder(object):
    """ La tâche principale du builder consiste à générer
    une instance de Param. Pour ce faire, il analyse les fichiers
    de config """

    #
    # Attributs récupérés du start.json
    # Valeurs par défaut définies.
    #
    display_enable = True
    seed = None
    seed_map = None
    iterations = -1
    nb_iterations_before_refresh = 1
    map_generation_params = None
    min_delay_between_refreshes = 1
    interaction_range = 1

    @classmethod
    def config_start(cls):
        """ Traite le fichier start.json pour configurer l'environnement
        de simulation """
        start_attributes = StartParser().get_start_params()
        # Récupération du nom de dossier à traiter
        Globals._simulation_name = start_attributes['launch']
        if not os.path.isdir(Globals.user_abs_simulation()):
            e = ParserError()
            e.add_message("Exception Message", "Directory not found")
            e.add_message("Filename", Globals.user_abs_simulation())
            e.add_message("Action", "Parsing start attributes")
            raise e

        # Génération de la map
        if 'map_seed' in start_attributes:
            cls.seed_map = start_attributes['map_seed']

        # Définition de la fonction de génération
        if 'map_generation' in start_attributes:
            if start_attributes['map_generation'] == 'perlin' :
                cls.__generate_map = cls.__alea_perlin
                # Parsing des paramètres pour la map
                if 'map_generation_params' not in start_attributes:
                    e = ParserError()
                    e.add_message("Exception Message", "Perlin generation need parameters")
                    e.add_message("Key error", "map_generation_params")
                    raise e
                cls.map_generation_params = start_attributes['map_generation_params']

                # Vérifie que tous les paramètres ont bien été donnés.
                generation_params = ["octaves", "frequency", "persistance"]
                for param in generation_params:
                    if param not in cls.map_generation_params:
                        e = ParserError()
                        e.add_message("Exception Message", "Param needed")
                        e.add_message("Param name", param)
                        raise e
            if start_attributes["map_generation"] == "user" :
                cls.__generate_map = cls.__user_generation

        # Délai entre chaque affichage
        if 'min_delay_between_refreshes' in start_attributes:
            cls.min_delay_between_refreshes = start_attributes['min_delay_between_refreshes']

        # Taille de la carte, obligatoire
        if 'map_size' in start_attributes:
            cls.map_size = start_attributes['map_size']
            if not isinstance(cls.map_size, (list, tuple)) \
               or len(cls.map_size) != 2:
                e = ParserError()
                e.add_message("Exception Message",
                    "map_size must be define 2 dimension (width, height)")
                e.add_message("Action", "Parsing start attributes")
                raise e
            if cls.map_size[0] != cls.map_size[1]:
                # TODO authoriser les maps rectangulaires.
                e = ParserError()
                e.add_message("Exception Message", "map_size must be squared")
                e.add_message("Action", "Parsing start attributes")
                raise e
        else:
            e = ParserError()
            e.add_message("Exception Message", "map_size not defined")
            e.add_message("Action", "Parsing start attributes")
            raise e

        # Définission du seed
        if 'seed' in start_attributes:
            cls.seed = start_attributes['seed']

        # Nombre d'itération de la simulation
        if 'iterations' in start_attributes:
            cls.iterations = start_attributes['iterations']
        else:
            e = ParserError()
            e.add_message("Exception Message", "iterations not defined")
            e.add_message("Action", "Parsing start attributes")
            raise e

        # Quantum d'affichage
        if 'nb_iterations_before_refresh' in start_attributes:
            cls.nb_iterations_before_refresh = start_attributes['nb_iterations_before_refresh']

        # Exportation ?
        if 'export' in start_attributes:
            SimExport.export_enabled = start_attributes['export']
            params = { "separator" : ";", "new_line" : "\n", "extension" :  "csv"}
            if 'export_param' in start_attributes:
                for key, value in start_attributes['export_param'].iteritems():
                    if key not in params:
                        e = ParserError()
                        e.add_message("Exception Message", "Export param wrong")
                        e.add_message("Key found", key)
                        e.add_message("Keys allowed", params.keys())
                        raise e
                    params[key] = value
            SimExport.export_param = params

        # Rayon d'action des interactions
        if 'interaction_range' in start_attributes:
            value = start_attributes['interaction_range']
            if value >= 0:
                cls.interaction_range = value

        # Mode graphique ou non
        if 'display_enable' in start_attributes:
            value = start_attributes['display_enable']
            if not value:
                cls.display_enable = False



    @classmethod
    def _get_entity_names(cls):
        """ Retourne les noms de toutes les entités configuré par
        l'utiliateur. Cette méthode analyse donc la structure
        de dossier de la configuration de la simulation """
        #path = os.path.join(Globals.user_abs_path(), "simulation", "entities")
        path = os.path.join(Globals.user_abs_simulation(), "entities")
        entities = []
        for item in os.listdir(path):
            if os.path.isdir(os.path.join(path, item)) \
               and item != "interactions":
                entities.append(item)
        return entities

    @classmethod
    def _get_terrain_names(cls):
        """ Retourne les différents types de terrain configurés
        dans terrain.json. """
        terrain_parser = TerrainParser()
        path = os.path.join(Globals.user_abs_simulation(), "terrain.json")
        return terrain_parser.read_terrains(path)

    @classmethod
    def __alea_generation(cls, sim_map):
        """ Génère la carte de la manière purement aléatoire.
        Répartit de manière aléatoire, avec une distribution uniforme, tous les types
        de terrains

        Arguments :
        sim_map -- La carte, contenant la grille ainsi que d'autres méthodes.
        """
        terrain_ids = range(len(SimUtils.get_terrain_names()))
        for index, _ in ndenumerate(sim_map.grid):
            x, y = index
            sim_map.grid[x][y] = SimUtils.random().choice(terrain_ids)

    @classmethod
    def __alea_perlin(cls, sim_map) :
        """ Génère la carte à l'aide d'un bruit de Perlin
        Répartit de manière aléatoire, avec une distribution de perlin tous les types
        de terrains. Utilise les paramètres "map_generation_params" du start.json pour
        configurer le bruit de perlin.

        Arguments :
        sim_map -- La carte, contenant la grille ainsi que d'autres méthodes.
        """
        import alea_perlin
        from alea_perlin import AleaPerlin

        AleaPerlin.fill_map(sim_map,
                            cls.map_generation_params["octaves"],
                            cls.map_generation_params["frequency"],
                            cls.map_generation_params["persistance"],
                            len(cls._get_terrain_names()),
                            cls.seed_map)

    @classmethod
    def __user_generation(cls, sim_map) :
        """ Génère une carte personnalisée à l'aide de configuration
        de l'utilisateur

        Arguments :
        sim_map -- La carte, contenant la grille ainsi que d'autres méthodes.
        """
        mapParser = MapParser()
        path = os.path.join(Globals.user_abs_simulation(), "map_generation.json")
        mapParser.read_configuration(path)

        # création d'un dictionnaire des terrains
        dict_terrains = dict()
        index = 0
        for name in SimUtils.get_terrain_names():
            dict_terrains[name] = index
            index = index + 1

        # déterminer le terrain par défaut
        default_terrain_index = dict_terrains[mapParser.default_terrain]

        # remplir la carte avec le terrain par défaut
        for index, _ in ndenumerate(sim_map.grid):
            x, y = index
            sim_map.grid[x][y] = default_terrain_index

        # ajouter les champs spéciaux
        for cell in mapParser.special_areas:
            sim_map.grid[cell[0]][cell[1]] = dict_terrains[cell[2]]

    @classmethod
    def __generate_map(cls, sim_map):
        """ Génération de la carte par défaut. """
        cls.__alea_generation(sim_map)

    @classmethod
    def get_params(cls):
        """ Cette méthode est consacré à créer une instance de Params
        pour que la classe Simulator puisse démarrer correctement
        une simulation"""

        SimUtils.random().seed(cls.seed_map)

        # Récupération des types de terrain
        terrain_objs = cls._get_terrain_names()

        # Enregistrer la carte
        SimUtils._register_maps(terrain_objs, cls.map_size)

        # Définition de la taille de la carte
        sim_map = SimulatorMap(cls.map_size[0], cls.map_size[1])
        # Génération du contenu de la carte
        cls.__generate_map(sim_map)

        SimUtils.random().seed(cls.seed)

        # Création des d’entités (création des instances)
        entities = set()
        entity_classes = []
        entity_colors = []
        entity_count = {}
        # Pour chaque type d'éntité
        for name in cls._get_entity_names():
            entity_class = new_entity_class(name, [str(terrain) for terrain in terrain_objs])
            entity_classes.append(entity_class)
        SimUtils._register_entities(entity_classes)

        for entity_class in entity_classes:
            instances = entity_class._create_instances()
            entity_count[entity_class] = len(instances)

            # Vérification du type des instances retournées
            if isinstance(instances, (list, tuple)):
                if len(instances) > 0 and not all([type(entity) == entity_class for entity in instances]):
                    e = ParserError()
                    e.add_message("Exception Message", "_create_instances corrupted")
                    e.add_message("Reason", "The list you return must be a list of Entity.")
                    e.add_message("List given", instances)
                    e.add_message("Entity", name)
                    raise e
            else:
                e = ParserError()
                e.add_message("Exception Message", "_create_instances corrupted")
                e.add_message("Reason",
                    "The list you return must be a list of Entity. {} found instead"\
                    .format(type(instances)))
                e.add_message("Entity", name)
                raise e
            entities.update(instances)
            entity_colors.append(entity_class._default_color)

        from loader.interactions import Interactions
        return Params(cls.iterations,
                      cls.display_enable,
                      entity_classes,
                      entity_colors,
                      entities,
                      sim_map,
                      cls.map_size,
                      cls.min_delay_between_refreshes,
                      cls.nb_iterations_before_refresh,
                      Interactions(),
                      cls.interaction_range,
                      cls.seed,
                      cls.seed_map)
