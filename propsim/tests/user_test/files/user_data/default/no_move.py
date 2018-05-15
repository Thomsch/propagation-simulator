# -*- coding: utf8 -*-
from simutils.trigger import *

class NoMove(Trigger):
    @staticmethod
    def is_performed(data):
        return True

    @staticmethod
    def action_performed(data):
        print "%s don't move !" % data.entity1.singular_name.capitalize()
