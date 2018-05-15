#!/usr/bin/env python
# -*-coding:utf-8-*-
from parser_error import ParserError

class ScriptError(ParserError):
    """ Erreur dans les scripts utilisateurs"""
    def __init__(self):
        super(ScriptError, self).__init__()
