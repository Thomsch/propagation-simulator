#!/usr/bin/env python
# -*-coding:utf-8-*-
from script_error import ScriptError

class MissingAttributeError(ScriptError):
    """ Un attribut nécessaire à la simulation est manquant. """
    def __init__(self):
        super(MissingAttributeError, self).__init__()
