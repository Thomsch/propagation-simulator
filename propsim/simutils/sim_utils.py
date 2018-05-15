#!/usr/bin/env python
# -*-coding:utf-8-*-
from simerrors import *
from simulator import sim_export

class SimUtils(object):
    """Fournit un ensemble de fonctions utilitaires permettant d'accéder
    à des données sur la simulation et l'état du simulateur.

    Cette classe est mise à disposition des scripts utilisateurs.
    """

    import random
    """ Instance de random.Random à utiliser pour toute génération de
    nombre aléatoire
    """
    rand = random.Random()
    """ Entités à insérer à la fin de l'itération courante """
    new_entity_buffer = []

    """ Référence du simulateur """
    __simulator = None
    """ Liste des différents types de terrains présents sur la carte """
    terrains = None
    """ Dimensions de la carte """
    map_bounds = None
    """ Liste des entités présentes dans la simulation """
    entities = None

    @classmethod
    def _register_simulator(cls, simulator):
        """ Permet à la classe d'accéder à certaines informations
        du simulateur pour pouvoir les retransmettre
        """
        cls.__simulator = simulator
        for entity in cls.new_entity_buffer:
            entity._need_refresh = True
            cls.__simulator.add_entity(entity)

    @classmethod
    def _register_maps(cls, terrains, map_bounds):
        """ Permet à la classe d'accéder aux informations sur la carte
        utilisée afin de pouvoir les retransmettre
        """
        cls.terrains = terrains
        cls.map_bounds = map_bounds

    @classmethod
    def _register_entities(cls, entities):
        """ Ajoute les différentes classes d'entités disponibles """
        cls.entities = {}
        for entity in entities:
            cls.entities[entity.__name__] = entity

    @classmethod
    def _get_entity_classes(cls):
        """ Donne les différentes classes spécialisées pour représenter
        les différents types d'entités de l'utilisateur
        """
        return cls.__simulator.params.entity_class

    @classmethod
    def random(cls):
        """ Retourne une instance de la classe random native Python
        initialisée avec les valeurs données par l'utilisateur.

        Devrait être utilisée partout dans le programme afin d'utiliser
        le même seed tout au long de l'exécution
        """
        return cls.rand

    @classmethod
    def randcolor(cls, tint=(0,0,0)):
        """Génère une couleur aléatoire selon une teinte donnée.

        Params:
        tint -- tuple de 3 entiers entre 0 et 255 (format RGB)

        Retour :
        Nom de la couleur en hexadécimal tel qu'utilisé par la GUI
        """

        # Sources :
        # http://stackoverflow.com/questions/43044/algorithm-to-randomly-generate-an-aesthetically-pleasing-color-palette
        # http://stackoverflow.com/questions/13998901/generating-a-random-hex-color-in-python

        def rand_byte(index):
            return (SimUtils.random().randrange(255) + tint[index]) // 2
        return '#%02X%02X%02X' % (rand_byte(0), rand_byte(1), rand_byte(2))

    @classmethod
    def is_in_map_area(cls, x, y):
        """ Indique si les coordonnées (x, y) données sont dans les
        limites de la carte (True) ou non (False).
        """
        (width, height) = cls.map_bounds
        return x >= 0 and x < width and y >= 0 and y < height

    @classmethod
    def get_terrain_type(cls, x, y):
        """ Retourne un objet de type Terrain permettant d'obtenir le nom
        dudit terrain d'après les coordonnées x, y données.
        Retourne None dans le cas ou la position ne se trouve pas dans la carte
        """
        try:
            return cls.__simulator.params.sim_map.get_terrain_type(x,y)
        except:
            return None

    @classmethod
    def get_map_bounds(cls):
        """ Donne les dimensions de la carte.

        Retourne le tuple (largeur, hauteur)
        """
        return cls.map_bounds

    @classmethod
    def get_terrain_names(cls):
        """ Donne les noms des différents types de terrain présents sur
        la carte.

        Retourne une liste de strings correspondants aux noms.
        """
        return [str(terrain) for terrain in cls.terrains]

    @classmethod
    def get_terrains(cls):
        """ Donne les informations des différents types de terrain
        présents sur la carte.

        Retourne une liste d'objets de type Terrain.
        """
        return cls.terrains

    @classmethod
    def get_entities(cls, x, y, when_out_of_bounds=None):
        """ Obtient la liste des entités en position (x,y).

        Retourne when_out_of_bounds si la position n'est pas sur la
        carte.
        """
        return cls.__simulator.get_entities(x, y) or when_out_of_bounds

    @classmethod
    def current_iteration(cls):
        """ Donne le numéro de l'itération actuelle. """
        return cls.__simulator.get_current_iteration()

    @classmethod
    def new_entity(cls, entity_type):
        """ Ajoute une entité du type donné dans la simulation.

        Params:
        entity_type -- nom du type d'entité à créer

        Le nom doit correspondre au nom du dossier utilisé pour définir
        l'entité.
        """
        if entity_type not in cls.entities:
            from simerrors import ParserError
            e = ParserError()
            e.add_message("Exception Message", "Entity not found")
            e.add_message("Types ", cls.entities)
            e.add_message("Entity name", entity_type)
            raise e

        entity = cls.entities[entity_type]()
        if cls.__simulator is not None :
            cls.__simulator.add_entity(entity)
        else:
            cls.new_entity_buffer.append(entity)
        return entity

    @classmethod
    def write_in_file(cls, file_name, object_dict):
        """ Ecrit les informations données dans le fichier de log de la
        simulation.

        Params:
        file_name -- nom du fichier
        object_dict -- dictionnaire donnant à chaque nom de colonne la
                        chaîne à écrire
        """
        if cls.__simulator is None:
            e = PropsimError()
            e.add_message("Exception Message", "Cannot write log file in _create_entities action")
            raise e
        sim_export.SimExport.write_file(file_name, object_dict)

    @classmethod
    def write_entity(cls, entity):
        """ Ecrit l'état actuel de l'entité dans le fichier de log de la
        simulation.
        """
        entity._log()

    @classmethod
    def kill_entity(cls, entity):
        """ Retire l'entité de la simulation """
        cls.__simulator.remove_entity(entity)

