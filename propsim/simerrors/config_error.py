#!/usr/bin/env python
# -*-coding:utf-8-*-
from propsim_error import PropsimError

class ConfigError(PropsimError):
    """ Erreur interne, devrait survenir si une exception a manquée d'être levée (bug de l'application donc)
    """

    def __init__(self):
        super(ConfigError, self).__init__()
