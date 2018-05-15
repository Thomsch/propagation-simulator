#!/usr/bin/env python
# -*-coding:utf-8-*-
import os
from config import Globals

def clean_workspace():
    """ Supprime les fichier de compilation et les fichiers __init__.py du domaine utilisateur.
    """
     # Suppression de tous les pyc à la fin, pour ne pas pertuber l'utilisateur.
    for root, subFolders, files in os.walk(Globals.user_abs_simulation()):
        for f in files:
            infos = os.path.splitext(f)
            if infos[1] != ".pyc":
                continue
            os.remove(os.path.join(root, f))

    # Supression des fichier __init__
    for root, subFolders, files in os.walk(os.path.join(Globals.user_abs_simulation())):
        for f in files:
            infos = os.path.splitext(f)
            if infos[0] != "__init__":
                continue
            os.remove(os.path.join(root, f))
