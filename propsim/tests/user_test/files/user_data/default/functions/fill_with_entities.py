# -*- coding: utf8 -*-
from simutils import *

class FillWithEntities(Function):
    def __init__(self):
        pass

    @staticmethod
    def call(data, _):
        (width, height) = SimUtils.get_map_bounds()
        instances = []
        for x in xrange(width):
            for y in xrange(height):
                new_entity = SimUtils.new_entity(data.entity1.__name__)
                new_entity._move_entity(x, y)
                instances.append(SimUtils.new_entity(data.entity1.__name__))
        return instances

