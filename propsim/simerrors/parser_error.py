#!/usr/bin/env python
# -*-coding:utf-8-*-
from propsim_error import PropsimError

class ParserError(PropsimError):
    """ Un attribut nécessaire à la simulation est manquant. """
    def __init__(self):
        super(ParserError, self).__init__()
