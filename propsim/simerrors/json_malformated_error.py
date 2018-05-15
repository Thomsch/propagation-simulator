#!/usr/bin/env python
# -*-coding:utf-8-*-
from json_error import JSONError

class JSONMalformatedError(JSONError):
    """ Erreur de syntaxe json """
    def __init__(self):
        super(JSONMalformatedError, self).__init__()
