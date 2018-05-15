#!/usr/bin/env python
# -*-coding:utf-8-*-
from script_error import ScriptError

class InvalidIdentifierError(ScriptError):
    """ Lorsque l'utilisateur utilise un identifier de méthode ou
    d'attribut qui n'est pas un indentificateur valide en python"""
    def __init__(self):
        super(InvalidIdentifierError, self).__init__()
