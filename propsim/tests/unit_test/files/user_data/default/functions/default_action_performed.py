# -*- coding: utf8 -*-
from simutils import *

class DefaultActionPerformed(Function):

    @staticmethod
    def call(data):
        # Utilisation des alias offert par le trigger
        # entity1 = (human, human1)
        data.human1.is_infected = True

