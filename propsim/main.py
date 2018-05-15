#!/usr/bin/env python
# -*-coding:utf-8-*-

# Programme: Propagation Simulator
# Auteurs  : Grégoire Decorvet, Hadrien Froger, Kevin Jaquier, 
#            Thomas Schweizer et Marcel Sinniger.
# Version  : 1.0
# But      : Fichier de lancement pour Propagation Simulator.

# Import pour la construction des entités
from builder.builder import Builder

# Import pour lancer l'interface graphique
from simulator.simulator import Simulator
from bridges.gui_bridge import GUIBridge
from gui.gui_handler import GUIHandler
from console.console import Console
from console.messages import Messages
from PySide.QtGui import QApplication

# Pour récupérer les arguments fournis au main
import sys
import shutil

# Pour construire et nettoyer l'espace utilisateur
from utils.build_workspace import *
from utils.clean_workspace import *

# Pour la gestion des exceptions
import sys, traceback


if __name__ == '__main__':

    # Copie des simulations par défaut dans le "home" de l'utilisateur
    # s'il n'y pas de simulations existantes
    if not os.path.exists(Globals.user_abs_path()):
        shutil.copytree(Globals.default_user_dir, Globals.user_root)

    # Initialisation de l'environnement graphique.
    application = QApplication(sys.argv)

    # Démarrage de la console
    console = Console("Launch console")
    console.show()
    console.push(Messages.main_001)

    exceptionOccurred = False
    try:
        # Préparation du user_data (fichier __init__.py)
        Builder.config_start()
        build_workspace()

        # Chargement des configurations
        params = Builder.get_params()
        console.push(Messages.main_002)
        console.push(Messages.main_003)
    except Exception as e:
        console.push_error("Error building simulation {}".format(Globals._simulation_name))
        # Affichage de la trace en console, de l'erreur dans le LOG.
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print exc_type.__name__.center(90, '-')
        print traceback.format_exc().splitlines()[-1]
        print "".ljust(90, '.')
        traceback.print_exception(exc_type,
            exc_value, exc_traceback, file=sys.stdout)
        print "".ljust(90, '-')

        console.push_error(exc_type.__name__)
        for line in str(e).split('\n'):
            console.push_error(line)
        exceptionOccurred = True

    # Démarrage seulement et seulement s'il n'y a pas d'erreur
    # pendant le chargement des configurations
    if not exceptionOccurred:
        # Démarrage du simulateur
        if params.display_enable:
            console.close()
            gui_bridge = GUIBridge()
            gui_handler = GUIHandler(gui_bridge)
            simulator = Simulator(gui_bridge, params)
            simulator.start()
        else:
            simulator = Simulator(None, params)
            simulator.start()

    # Fermeture propre de l'application. (Laisse l'environnement utilisateur sans .pyc et __init__.py)
    clean_workspace()

    # C'est PyInstaller qui veut vraiment sys.exit et pas simplement
    # exit. Du coup, ne pas toucher la ligne suivante
    sys.exit(application.exec_())
