#!/usr/bin/env python
# -*-coding:utf-8-*-
""" Super classe pour tous les Trigger afin de valider que
les sous-classes définissent bien des méthodes statiques
correspondant à notre utilisation de Trigger.
Permet en d'autre sorte de définir une classe abstraite qui
définit des méthodes statiques abstraites.
"""
from  simerrors import *
from data import Data
from sim_utils import SimUtils

random = SimUtils.random()

class Trigger(object):
    """ Super-classe de tous les Trigger. Permet de vérifier
    la présence des méthodes statiques is_performed et action_performed """

    @classmethod
    def _check_trigger(cls):
        """  Permet d'avoir un comportement de classe
        abstraite au niveau des méthodes de classes (statiques)
        """
        is_performed_exists = False
        action_performed_exists = False
        # tests que les méthodes is_performed et action_performed existent
        # bels et bien.
        for class_attribute in cls.__dict__.keys():
            if class_attribute == 'is_performed':
                is_performed_exists = True
            elif class_attribute == 'action_performed':
                action_performed_exists = True
            if is_performed_exists and action_performed_exists:
                break

        if not is_performed_exists or not action_performed_exists:
            ex = ActionMalformatedError()
            ex.add_message("Exception Message", "Trigger can not be instanciate")
            ex.add_message("Missing static method", 'is_performed' if action_performed_exists else 'action_performed')
            raise ex

