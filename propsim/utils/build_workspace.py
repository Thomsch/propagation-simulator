#!/usr/bin/env python
# -*-coding:utf-8-*-
import os
from config import Globals

def build_workspace():
    """ Crée un fichier __init__.py dans tous les dossiers d'entités
    afin de rendre les scripts locaux importable"""
    for root, dirs, filenames in os.walk(Globals.user_abs_simulation()):
        with open(os.path.join(root, "__init__.py"), "w"):
            pass
