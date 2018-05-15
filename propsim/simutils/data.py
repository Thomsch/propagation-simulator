#!/usr/bin/env python
# -*-coding:utf-8-*-

""" Permet de définir un conteneur qui sera utilisé par les Triggers
afin de lancer leurs fonctions statiquement tout en gardant un scope.
Par cette méthode, nous réduisons considérablement la place mémoire
allouée.
"""
from simerrors import *

class Data(object):
    """ Conteneur possédant toutes les informations nécessaires lors
    d'un appel de fonction ou de trigger. Résume le scope de
    l'utilisateur au sein d'une fonction.
    """

    def __init__(self):
        """ Création des attributs nécessaires aux Triggers"""
        self.entity1 = None
        self.entity2 = None
        self.terrains = None

    def _clear(self):
        """ Prépare le conteneur à recevoir de nouvelles informations. """
        self.entity1 = None
        self.entity2 = None
        self.terrains = None

    def __getattr__(self, name):
        """ Permet les alias pour les triggers. Ainsi l'utilisateur
        peut appeler les entités sous différents nom de manière transparente.
        Les alias sont crées d'après le type d'entité (Entity#__class_identifier__)

        Ainsi, pour entité nommée Human, nous avons comme alias :
            entity1 : entity1, human1, human
            entity2 : entity2, human2
        """
        if self.entity1 is None and self.entity2 is None :
            ex = PropsimError()
            ex.add_message("Exception Message", "Data malformated")
            ex.add_message("Exception Level", "FATAL ERROR")
            raise ex

        entity1_name = '-'
        entity2_name = '-'

        if self.entity1 is not None :
            entity1_name = self.entity1.__name__.lower()
        if self.entity2 is not None :
            entity2_name = self.entity2.__name__.lower()

        if self.entity1 is not None :
            if name == entity1_name + '1' or\
                name == "entity1" or\
                (name != entity2_name and name == entity1_name):
                return self.entity1

        if self.entity2 is not None :
            if name == entity2_name + '2' or\
                name == "entity2" or\
                (name != entity1_name and name == entity2_name):
                return self.entity2

        #
        # On tente d'accéder à un attribut qui n'existe pas
        #
        ex = InvalidIdentifierError()
        expected = list()
        if self.entity1 is not None:
            if name == entity1_name + '1':
                expected.append(entity1_name + '1')
            elif name != entity2_name and name == entity1_name :
                expected.append(entity1_name + '1', entity1_name)

        if self.entity2 is not None:
            if name == entity2_name + '2':
                expected.append(entity2_name + '2')
            elif name != entity1_name and name == entity2_name :
                expected.append(entity2_name + '2', entity2_name)

        ex.add_message("Exception Message", "Unknown identifier")
        ex.add_message("Identifier", name)
        ex.add_message("Entity1", entity1_name)
        ex.add_message("Entity2", entity2_name)
        ex.add_message("Expected", ", ".join(expected) if len(expected) > 0 else "[]")

        if self.terrains is not None:
            ex.add_message("Terrains", self.terrains)
        ex.add_title("Error accessing Data", "=")
        raise ex
