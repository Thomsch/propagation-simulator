# -*- coding: utf8 -*-
from simutils import *

class Piquer(Trigger):
    @staticmethod
    def is_performed(data):
        """ L'action est appelée avec 0.66% de probabilité et si
        l'humain n'est pas déjà infecté
        """
        return SimUtils.random().random() < 0.66 \
               and not data.humain._is_affected

    @staticmethod
    def action_performed(data):
        """ Déplacer l'entité sur la carte selon un pas
        humanoïde cohérent
        """
        data.humain._color = data.humain.color_infected
        data.humain._is_affected = True
        data.moustique.infected_count += 1