#!/usr/bin/env python
# -*-coding:utf-8-*-
""" Fonction permettant de créer une nouvelle classe d'entité,
construite par une métaclasse avec les paramètres donnés.

Le but de la métaclasse sera de créer une classe correspondant aux
configurations de l'utilisateur. Nous y parsons et chargeons donc les
différentes méthodes (actions) définies, et préparons un "modèle" de
dictionnaire que chaque instance crée par la classe pourra copier.

Cette classe définit aussi des méthodes "par défaut". En effet, la
métaclasse ayant tous les pouvoir sur la classe, elle peut écraser la
définition des méthodes par des méthodes utilisateur. Afin de sécuriser
quelque peu le procédé, nous avons restreint l'utilisateur :

- Il ne peut définir que des méthodes privées ou protégées
- Les méthodes protégées doivent être autorisées par la métaclasse (voir
  EntityMetaclass.overrides)

Ainsi seule une liste de méthodes définies pour être surchargées,
garantissant un peu de sécurité quand à la définissions de méthodes dans
cette classe.
"""
from entity import Entity
from entity_metaclass import EntityMetaclass
from simerrors import *
from simutils.sim_utils import SimUtils

def new_entity_class(entity_name, terrains) :
    """ Crée un nouvelle classe pour le nom et le terrain donné.
    """

    class AnonymousEntity(Entity):
        """ Entité définie par l'utilisateur. Les script json
        d'attributs et d'actions d'une entité contribue à la
        construction d'une nouvelle classe, sur le support de
        AnonymusEntity.

        Il s'agit donc d'un squelette d'entité, sur lequel l'utilisateur
        peut se baser. Elle définit des attributs et méthodes par
        défaut, qui pourront être potentiellement surchargé.

        # Attributs, système de double tampon.
        Tous les attributs de cette classe sont doublé, afin de faire un
        système d'édition en deux temps. Durant un pas de simulation, un
        attributs d'une entité peut changer plusieurs fois. Nous avons
        donc décider de doubler les attributs, pour que la simulation
        reste la plus cohérente possible. Nous avons donc une version
        d'attribut "récente", qui est l'état de l'attribut à la fin du
        pas précédent. Cette version est "en lecture". La deuxième
        version de l'attribut est uniquement pour l'écriture, qui sera
        appliquée à la fin du pas de simulation.

        Cela permet de simuler une sorte de double tampon, ainsi
        l'entité Human avec un attribut age se comportera ainsi :

            >>> import simutils
            >>> human = simutils.new_entity("Human")
            >>> human.age
            20
            >>> human.age += 2          # l'age "futur" vaut 22
            >>> human.age
            20
            >>> human._swap()           # Fin du pas de simulation
            >>> human.age
            22

        On peut donc voir que l'utilisation extérieur des attributs
        d'une entité est complètement transparente.

        ## Changements doubles
        Cette politique de modification d'attribut possède un problème.
        En cas de changement double dans un pas de simulation,
        l'attribut est écrasé. Afin de simplifier et de rendre la
        simulation cohérente, nous avons pris le parti d'appliquer les
        changements "doubles" avec une probabilité purement aléatoire.

        # Méthodes surchargeables par l'utilisateur
        Afin de permettre une utilisation plus souple de notre
        application, les méthodes protégées pourront être surchargées
        par l'utilisateur via des scripts JSON, et les méthodes privées
        seront elles fixes.
        """

        # Demande à la metaclasse de construire l'entité d'après le nom
        # d'entité et les terrains demander lors de l'appel de la
        # fonction new_entity_class
        __metaclass__ = EntityMetaclass(entity_name, terrains)

        @classmethod
        def _create_instances(cls):
            """ Crée des instances pour l'entité.
            Crée un fichier de log contenant les paramètre de départ. """
            insts = cls()._create_entities()

            if len(insts) > 0 :
                cls._default_color = insts[0]._color
            for inst in insts:
                inst._swap()
            return insts

        """ Définit si cette instance peut ajouter des attributs
        ATTENTION : Le nom de l'attribut est utilisé dans __setattr__,
        NE PAS renommer
        """
        _frozen = False

        def __init__(self):
            """ Appelée une fois que la métaclasse (__metaclass__) a
            parsé les différents fichiers utilisateur. Cette méthode
            permet d'ajouter une copie des attributs dans son
            dictionnaire et de copier le dictionnaire pour gérer la
            politique de modification d'attributs.
            """
            self.__frozen = False

            # Crée un dictionnaire pour contenir le tampon des
            # différents attributs. Ce dictionnaire se construit au fur
            # et à mesure, ainsi un attribut constant ne figurera jamais
            # dans ce dictionnaire.
            self.__future__ = {}
            self._need_refresh = False

            self.__frozen = True

        def _init_entity(self):
            """ Par défaut ne fait rien de particulier. Une fois
            surchargée, permet de faire une fonction d'initialisation
            des entités, individuellement. En effet les scripts
            utilisateurs ne permettent de définir que des valeurs
            d'attributs par type d'entité.
            """
            pass

        def _move_entity(self, new_x, new_y):
            """ Déplace l'entité en vérifiant sa position dans la carte. """
            if SimUtils.is_in_map_area(new_x, new_y):
                self._x = new_x
                self._y = new_y

        def _get_pos(self):
            """ Donne la position x,y actuelle de l'entité sur la carte. """
            return (self._x, self._y)

        def _apply_actions(self, terrain_id):
            for action in self.__actions__[terrain_id]:
                action(self)

        def _export(self):
            """ Action d'export par défaut.
            Export tous les attributs de l'entité """
            SimUtils.write_entity(self)

        def _get_attributes(self):
            """ Donne tous les attributs de l'entité """
            attributes = dict()
            for name in self.__attributes_name__:
                attributes[name] = self._get_attribute(name)
            return attributes

        def _get_attribute(self, attribute_name):
            """ Donne la valeur d'un attribut de l'entité """
            return self.__getattribute__(attribute_name)

        def _swap(self):
            """ Applique les modifications des attributs sur l'entité.
            Retourne Vrai si des attributs demandant un rafraîchissement de la
            vue graphique est nécessaire.
            """
            self.__dict__.update(self.__future__)
            self.__future__ = {}
            need_refresh = self._need_refresh
            self._need_refresh = False
            return need_refresh

        def _is_active(self):
            return not self.__dict__.has_key("_inactive")

        def _set_active(self, active):
            if active:
                if self.__dict__.has_key("_inactive"):
                    self.__dict__.pop("_inactive")
            else:
                self.__dict__.setdefault("_inactive")

        def _create_entities(self):
            """ Méthode par défaut, surchargeable, permettant de
            créer 50 entités sur la carte.
            """
            default_number = 50
            instances = []
            for i in range(default_number):
               instances.append(type(self)())
            return instances

        def __setattr__(self, key, value):
            """ Modifie un attribut qui n'existe pas (assignation)
            Lors de la création de l'entité, nous autorisons l'ajout
            d'attribut, mais après création nous devons l'interdire """
            if key != "_AnonymousEntity__frozen"\
                    and self.__frozen\
                    and not hasattr(self, key):
                e = InvalidIdentifierError()
                e.add_message("Exception Message", "Unknow attribute")
                e.add_message("Attribute Name", key)
                e.add_message("Entity Name", self.__name__)
                raise e
            object.__setattr__(self, key, value)

        def _log(self, attribute_list = None):
            """ Ecrit dans un fichier de log les attributs de l'entité.
            Par défaut exporte tout, sauf les attributs constants
            _colors, _labels, _name, _plural_name """
            if attribute_list == None:
                # Comportement par défault
                attribute_list = []
                attribute_list.extend(self.__attributes_name__)
                # Constantes à supprimer des logs
                attribute_list.remove('_color')
                attribute_list.remove('_labels')
                attribute_list.remove('_name')
                attribute_list.remove('_plural_name')

            # Vérification du type de la liste donnée
            if not isinstance(attribute_list, (tuple, list)):
                e = PropsimError()
                e.add_message("Exception Message", "Type error for _log(attribute_list = None)")
                e.add_message("Type Expected", "list")
                e.add_message("Type Found", type(attribute_list).__name__)
                raise e

            values = dict()
            # Vérification de la validité des clés.
            for attribute in attribute_list :
                if attribute not in self.__attributes_name__:
                    e = InvalidIdentifierError()
                    e.add_message("Exception Message", "Unknow attribute for export")
                    e.add_message("Attribute Name", attribute)
                    e.add_message("Entity Name", self.__name__)
                    raise e
                values[attribute] = self.__getattribute__(attribute)

            SimUtils.write_in_file(self.__name__, values)



        def __str__(self):
            """ Retourne tous les attributs disponibles,
            ainsi que les attributs définit par la métaclasse. """
            size_console = 80
            sb = []
            sb.append(u"# Actions")
            for terrain_id, terrain_actions in enumerate(self.__actions__):
                terrain_name = self.__terrains__[terrain_id]
                actions_names = [(action.__name__ \
                    if action is not None else "None")
                    for action in terrain_actions]
                sb.append(u"\t__{} __\t{}"\
                    .format(unicode(terrain_name),
                                    u", ".join(sorted(actions_names))))
            sb.append(u"# Attributes")
            for key in sorted(self.__dict__.iterkeys()):
                if len(key) > 1 and key[0] == '_' and key[1] == '_':
                    continue
                value = self.__dict__[key]
                if isinstance(value, (tuple, list)):
                    value = u", ".join(sorted(value))
                sb.append(u"\t{key} : {value}".format(key=key, value=value))
            sep =  "\n" + "".center(size_console, "=") + "\n"
            title = self.__name__.upper().center(size_console, "=")
            # TODO indiquer les interactions dispo sur l'entité.

            content = unicode(u"\n".join(sb))
            return (title + '\n' + content + sep).encode('utf-8')

    AnonymousEntity.__name__ = entity_name
    # Retourne la nouvelle classe telle que définie par l'utilisateur.
    return AnonymousEntity
