#!/usr/bin/env python
# -*-coding:utf-8
from loader.parser import interaction_parser
from loader.parser.interaction_parser import InteractionParser

class InteractionsMetaclass(object):

    def __init__(self):
        super(InteractionsMetaclass, self).__init__()

        self.interactions = dict()
        self.interaction_parser = InteractionParser(self.__add_interaction)
        self.interaction_parser.read_interactions()
        self.class_attributes = dict()
        self.class_attributes['_generate_key'] = self.__generate_key
        self.class_attributes['_interactions'] = self.interactions

    def __call__(self, name, bases, dct):
        dct.update(self.class_attributes)
        new_class = type(name, bases, dct)
        return new_class

    def __generate_key(self, entity1, entity2):
        """ Crée une clés qui permet de représenter un lien entre
        deux entités de manières équivoques. La clé pour entité A et B sera la
        même que celle pour B et A. """
        return ">".join(sorted([entity1, entity2])).lower()

    def __add_interaction(self, entity1, entity2, interaction):
        """ Ajoute une interaction entre les deux entités.

        Arguments :
        entity1 -- la première entité
        entity2 -- la deuxième entité
        interaction -- l'interaction à déclencher lors de la rencontre des
            deux entités.

        """
        key = self.__generate_key(entity1, entity2)
        if not self.interactions.has_key(key):
            self.interactions[key] = list()
        self.interactions[key].append(interaction)


