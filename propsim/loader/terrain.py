#!/usr/bin/env python
# -*-coding:utf-8-*-

from __future__ import division

from simutils import SimUtils

class Terrain(object):
    """ Représentation d'un terrain avec ses attributs """

    def __init__(self, name, attributes):
        self.name = name
        # Récupère la couleur spécifiée, ou une couleur aléatoire si
        # non-spécifiée
        self.color = attributes.get('color', SimUtils.randcolor((255,255,255)))

    def __str__(self):
        return self.name
