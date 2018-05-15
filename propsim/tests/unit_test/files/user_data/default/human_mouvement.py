# -*- coding: utf8 -*-
from simutils.trigger import *

class HumanMouvement(Trigger):
    @staticmethod
    def is_performed(data):
        """ L'action est toujours appelée une fois appelée
        """
        return True

    @staticmethod
    def action_performed(data):
        """ Déplacer l'entité sur la carte selon un pas
        humanoïde cohérent
        """
        x = data.entity1._lat
        y = data.entity1._lng
        data.entity1._move_entity(x + 1, y + 1)
