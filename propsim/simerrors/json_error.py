#!/usr/bin/env python
# -*-coding:utf-8-*-
from parser_error import ParserError
class JSONError(ParserError):
    """ Désigne une erreur fatale de parsing des scripts utilisateur.
    """

    def __init__(self):
        super(JSONError, self).__init__()
