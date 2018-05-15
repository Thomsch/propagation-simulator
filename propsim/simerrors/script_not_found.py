#!/usr/bin/env python
# -*-coding:utf-8-*-
from script_error import ScriptError

class ScriptNotFoundError(ScriptError):
    """ Fichier de script introuvable (fichier *.py) """
    def __init__(self):
        super(ScriptNotFoundError, self).__init__()
