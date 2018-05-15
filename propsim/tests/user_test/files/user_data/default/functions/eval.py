# -*- coding: utf8 -*-
from simutils import *

class Eval(Function):
    def __init__(self):
        pass

    @staticmethod
    def call(data, python_code):
        return self.eval(pyhon_code)
