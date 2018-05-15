#!/usr/bin/env python
# -*-coding:utf-8-*-

""" Permet de construire un classe d'entité. Le schéma de création d'une
entité se fait donc ainsi :

- EntityMetaclass > Entity > instance de entités.

Nous avons donc ici accès uniquement aux attributs statiques de
l'entité, c'est à dire :

- Aux attributs statiques
- Aux méthodes statiques et de classes
- Aux méthodes d'instances

En effet une méthode d'instance n'est autre qu'une fonction qui prend en
premier paramètre self, et étant donné que le type n'est pas déterminer
à la compilation, nous n'avons pas besoin de connaître la composition de
l'instance pour pouvoir lui définir des méthodes.

"""
from parser import *
from simerrors import *

class EntityMetaclass(object):
    """ Permet de créer une nouvelle classe d'entité selon les besoins
    de l’utilisateur. Gère les différents sucre syntaxique pour le
    parser, et gère partiellement les exceptions utilisateurs.
    """
    overrides = ['_init_entity', '_create_entities', '_export']

    def __init__(self, entity_name, terrains):
        super(EntityMetaclass, self).__init__()
        """ Le nom de l'entité, utilisé pour trouver le dossier dans
        lequel sont définit les attributs/actions de l'entité """
        self.entity_name = entity_name

        """ La liste de terrain utilisé dans la simulation """
        self.terrains = terrains

        """ Tous les attributs que les instances posséderont dans leurs
        __dict__ """
        self.instance_attributes = {}

        """ Tous les attributs de classes de l'entité (comme les
        méthodes) """
        self.class_attributes = {}

        """ Références sur action, indexés sur des terrains. Permet de
        connaître quel action appliquer dans quelle situation """
        self._actions = [] * len(terrains)
        for terrain in terrains:
            self._actions.append([])

        """ Parser d'attribut, permet de checker les noms des identifieurs,
        et la validité de la surcharge des attributs """
        self.attr_parser = AttrParser(self.entity_name)

        """ Parser d'action pour charger dynamiquement tous les fichiers
        définissant les actions """
        self.action_parser = ActionParser(\
            self.entity_name,\
            self.__add_action,\
            self.__register_action) # Nous transmettons des pointeurs
                                    # sur méthodes, afin d'avoir un
                                    # temps d'accès optimisé lors de
                                    # l'appel. (pas besoin de résoudre
                                    # le Entitymetaclass.*)

        # Parsing des scripts utilisateurs
        self.instance_attributes.update(\
            self.attr_parser.read_attributes())
        self.action_parser.read_actions(EntityMetaclass.overrides)

        # Ajout d'attributs de classes privées aux entités
        self.class_attributes["__name__"] = entity_name
        self.class_attributes["__attributes_name__"] = self.instance_attributes.keys()
        self.class_attributes["__actions__"] = self._actions[:]
        self.class_attributes["__terrains__"] = self.terrains
        self.class_attributes["__future__"] = {}
        self.class_attributes["__userattr__"] = self.instance_attributes

        self.class_attributes.update(self.instance_attributes)

    def __call__(self, name, bases, dct):
        """ Méthode appelée lorsque l'on appelle la classe, comme par
        exemple :

            >>> EntityMetaclass("Human")

        Permet d'ajouter des méthodes à la classes. Cependant, il n'est
        pas possible de manipuler tout de suite les instances, car il
        s'agit de construction de classes, qui elles-mêmes créerons des
        instances.

        Nous laissons donc la responsabilité de la classes crées de
        composer son dictionnaire d'attributs. Afin de lui facilité la
        tâche, nous lui mettons à disposition des attributs de classes
        supplémentaires (voir EntityMetaclass.class_attributes )
        """
        # Fusion de tous les attributs de classes (méthodes et attributs statiques)
        dct.update(self.class_attributes)
        new_class = type(name, bases, dct)
        return new_class

    def __add_action(self, action_name, action_function):
        """ Ajoute une action (méthode d'instance) à la classe. L'appel
        de cette action effectue le is_performed, puis si il y a lieu
        d'être, effectue le action_performed.

        Arguments : action_name -- le nom sous lequel pourra être appelé
        la méthode action_function -- méthode à ajouter.

        """
        self.class_attributes[action_name] = action_function

    def __register_action(self, terrain, action_pointer):
        """ Ici nous enregistrons un pointeur sur méthode pour
        un terrain donné. Ainsi, chaque terrain à une liste d'action à
        appliquer

        Arguments :
        terrain -- le terrain sous lequel l'action est valable.
        action_pointer -- la méthode déclenchée lors de l'action

        """
        # On trouve de quel indice de terrain il s'agit
        terrain_id = -1
        terrains_name = [str(t) for t in self.terrains]

        try:
            terrain_id = terrains_name.index(str(terrain))
        except ValueError as e :
            # Le terrain n'existe pas
            ex = TerrainNotFound()
            ex.add_message("Exception Message", e)
            ex.add_message("Terrain unknown", terrain)
            ex.add_message("Terrains accepted", terrains_name)
            raise ex

        # ajoute l'action appropriée
        self._actions[terrain_id].append(action_pointer)


