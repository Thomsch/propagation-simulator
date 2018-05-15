# -*- coding: utf8 -*-
from simutils import *

class CreationInstanceNum(Function):
    def __init__(self):
        pass

    @staticmethod
    def call(data, number):
        instances = list()
        for i in range(number):
           instances.append(SimUtils.new_entity(data.entity1.__name__))
        return instances

