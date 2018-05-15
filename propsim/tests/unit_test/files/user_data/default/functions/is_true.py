# -*- coding: utf8 -*-
from simutils import Function
class IsTrue(Function):
    def __init__(self):
        pass

    @staticmethod
    def call(data, *args):
        # TODO envisager d'utiliser un eval de littéraux
        # uniquement.
        for eval_arg in args:
            if not Function.eval(data, eval_arg):
                return False
        return True
