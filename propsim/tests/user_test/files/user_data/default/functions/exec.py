# -*- coding: utf8 -*-
from simutils.function import *

class Exec(Function):
    def __init__(self):
        pass

    @staticmethod
    def call(data, *codes):
        for python_code in codes:
            Function.execute(data, python_code)
