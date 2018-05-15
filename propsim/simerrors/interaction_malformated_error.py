#!/usr/bin/env python
# -*-coding:utf-8-*-

from script_error import ScriptError
class InteractionMalformatedError(ScriptError):
    """ Lorsque l'action définie dans un fichier *.json est
    mal définie. """
    def __init__(self):
        super(InteractionMalformatedError, self).__init__()
