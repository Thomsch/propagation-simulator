# -*- coding: utf8 -*-
from simutils import *

class InvalidTriggerExec(Trigger):

    @staticmethod
    def is_performed(data):
        return 0 / (1-1)

    @staticmethod
    def action_performed(data):
        print "nothing !"


