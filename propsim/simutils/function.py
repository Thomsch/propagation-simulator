#!/usr/bin/env python
# -*-coding:utf-8-*-
""" Définit une des deux fonctions de Trigger.
Cette classe permet essentiellement de faciliter l'utilisation du programme.
Lors de l'utilisation intensive d'une même fonction is_performed ou action_performed
dans de nombreux Trigger, nous permettons de centraliser une partie du Trigger dans
une fonction, afin de permettre une meilleure réutilisabilité de code.
"""
from  simerrors import *
from sim_utils import SimUtils

random = SimUtils.random()

class Function(object):
    """ Fonction composant un Trigger anonyme, créer à la volée
    pour lancer ses fonctions.
    Cette classe n'offre aucun environnement d'instance, afin de limiter
    l'utilisation de la mémoire, qui peut s'avérer critique dans le cadre des
    simulations.
    """

    @staticmethod
    def eval(data, python_code):
        """ Evalue le code donné en paramètre, avec comme scope les
        différents alias de entity1 et entity2 """
        # Configuration du namespace disponible dans la méthode éval
        locals()["random"] = random
        locals()["utils"] = SimUtils

        if data.entity1 is not None:
            entity1_name = data.entity1.__name__.lower()
            locals()["entity1"] = data.entity1
            locals()[entity1_name] = data.entity1
            locals()[entity1_name+"1"] = data.entity1

        if data.entity2 is not None:
            entity2_name = data.entity2.__name__.lower()
            locals()["entity2"] = data.entity2
            locals()[entity2_name+"2"] = data.entity2
            if type(data.entity1) != type(data.entity2):
                locals()[entity2_name] = data.entity2

        return eval(python_code)

    @staticmethod
    def execute(data, python_code):
        """ Execute le code python donné en paramètre avec
        un scope permettant les alias dans les scripts utilisateurs. """
        # Configuration du namespace disponible dans la méthode éval
        locals()["random"] = random
        locals()["utils"] = SimUtils

        if data.entity1 is not None:
            entity1_name = data.entity1.__name__.lower()
            locals()["entity1"] = data.entity1
            locals()[entity1_name] = data.entity1
            locals()[entity1_name+"1"] = data.entity1
        if data.entity2 is not None:
            entity2_name = data.entity2.__name__.lower()
            locals()["entity2"] = data.entity2
            locals()[entity2_name+"2"] = data.entity2
            if type(data.entity1) != type(data.entity2):
                locals()[entity2_name] = data.entity2
        if not isinstance(python_code, (str, unicode)):
            ex = ScriptError()
            ex.add_message("Exception Message", "Cannot execute code given, bad type")
            ex.add_message("Type found", type(python_code).__name__)
            ex.add_message("Type expected", "str")
            raise ex

        exec(python_code)

    @classmethod
    def _check_function(cls):
        """  Permet d'avoir un comportement de classe
        abstraite au niveau des méthodes de classes (statiques)
        """
        for class_attribute in cls.__dict__.keys():
            if class_attribute == 'call':
                return

        ex = ActionMalformatedError()
        ex.add_message("Exception Message", "Function can not be instanciate")
        ex.add_message("Missing static method", 'call')
        raise ex
