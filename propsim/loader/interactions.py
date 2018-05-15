#!/usr/bin/env python
# -*-coding:utf-8
from loader import interactions_metaclass
from loader.interactions_metaclass import InteractionsMetaclass

class Interactions(object):
    """ Met à disposition :

    1. cls._interactions le dictionnaire liant un couple d'entité à leurs interactions.
    2. cls_generate_key
        Pour trouver la clé dans le dictionnaire
        _interactions correspondant à deux entités.

    """
    __metaclass__ = interactions_metaclass.InteractionsMetaclass()

    def apply_interactions(self, entity1, entity2):
        """ Applique toutes les interactions liant le type des entités données

        Arguments :
        entity1, entity2 -- Les entités concernées

        """
        key = self._generate_key(entity1.__name__, entity2.__name__)
        if self._interactions.has_key(key):
            for interaction in self._interactions[key]:
                #TODO Ajouter un gestionnaire d'exception potable
                interaction(entity1, entity2)

    @classmethod
    def get_interactions_description(cls):
        """ Donne une table décrivant toutes les interactions intervenant dans la simulation
        avec les entités concernées. Utile à des fins de debug """

        description = list()
        description.append("{:<20s}\t{:<20s}\t{}".format("Entity 1", "Entity 2", "Interaction name"))
        for key, interactions in cls._interactions.iteritems():
            (entity1, entity2) = key.split('>')
            for interaction in interactions:
                description.append("{:<20s}\t{:<20s}\t{}".format(entity1, entity2, interaction.__name__))
        return "\n".join(description)
