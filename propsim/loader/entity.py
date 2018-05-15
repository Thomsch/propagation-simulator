#!/usr/bin/env python
# -*-coding:utf-8

""" Définit une superclasse pour toutes les entités
permet de définir une interface commune à toutes
les entités.
"""

from abc import ABCMeta, abstractmethod

class Entity(object):
    """ Interface regroupant toutes les entités"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def _swap(self):
        pass

    @abstractmethod
    def _apply_actions(self, terrain_id):
        pass

    @abstractmethod
    def _is_active(self):
        pass

    @abstractmethod
    def _set_active(self, active):
        pass
