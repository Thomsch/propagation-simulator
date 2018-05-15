#!/usr/bin/env python
# -*-encoding:utf8-*-

"""
Gestionnaire de l'interface graphique, Il s'occupe de la gestion de la partie
graphique de programme et le l'échange d'information entre la simulation
et l'interface.
"""

import threading
from config.globals import Globals
from bridges.qml_bridge import QMLBridge
from image_provider import ImageProvider
from gui.qml_view import QMLView
from gui.timer import Timer
from data.stat_item import StatItem

from PySide.QtDeclarative import QDeclarativeView
from PySide.QtGui import QGraphicsView
from PySide.QtCore import Slot
from PySide.QtGui import QIcon
import os

PROVIDER_NAME = "prosim"
MODEL_NAME = "list"
WINDOW_ICO_PATH = os.path.join("simutils", "icon_256x256.png")

class GUIHandler(threading.Thread):
    """
    Classe de contrôle et de liaison pour l'interface graphique en QML.
    """
    def __init__(self, gui_bridge):
        """
        Ajoute tous les objets nécessaires au fonctionnement de l'interface.
        Certaines instructions doivent se faire avant d'autre à cause de la
        façon dont Qt gère les fenêtres et le chargement du QML.
        """
        threading.Thread.__init__(self)
        self.__gui_bridge = gui_bridge
        self.__view = QMLView()
        self.__engine = self.__view.engine()
        self.__provider = ImageProvider(self)

        # Mesure du nombre d'images par secondes.
        self._frames = 0 # Compte le nombre de frames.
        self._timer = Timer(1) # Timer avec 1 seconde de délai.
        self._framerate= StatItem("FPS: ", 0)


        self.__next_data = None
        self.__map_data = None

        self.__init_engine()
        self.__init_view()

        self.__qml_bridge = QMLBridge(self.__view, [])
        self.__gui_bridge.register_gui(self)

        self.__view.show()

        # Evénements pour la synchronisation concurrente.
        self.event_stop = threading.Event()
        self.event_render_updated = threading.Event()

        # Connection des signaux
        self.__qml_bridge.on_stopped.connect(self.__stop)
        self.__qml_bridge.on_played.connect(self.__play)
        self.__qml_bridge.on_paused.connect(self.__pause)
        self.__qml_bridge.on_render_updated.connect(self._render_updated)
        self._timer.on_action.connect(self._update_framerate)
        self.__view.closing.connect(self.__stop)

        # Lancement du thread de gestion de l'interface graphique.
        self.start()

    def __init_view(self):
        """
        Paramétrisation de la vue.
        """
        self.__view.setCacheMode(QGraphicsView.CacheBackground)
        self.__view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.__view.setOptimizationFlags(QGraphicsView.DontAdjustForAntialiasing)
        self.__view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
        self.__view.setMinimumHeight(self.__view.height())
        self.__view.setMinimumWidth(self.__view.width())
        self.__view.setWindowTitle("Propagation Simulator - " + Globals._simulation_name)
        self.__view.setWindowIcon(QIcon(WINDOW_ICO_PATH))

    def __init_engine(self):
        """
        Paramétrisation du moteur d'application.
        """
        self.__engine.addImageProvider(PROVIDER_NAME, self.__provider);

    def get_next_data(self):
        """
        Renvoie les entités mises à jour pour l'interface.
        """
        if self.is_alive():
            return self.__next_data
        else:
            return None

    def get_map_data(self):
        """
        Renvoie la carte pour l'interface.
        """
        if self.is_alive():
            return self.__map_data
        else:
            return None

    def get_entities(self):
        """
        Retourne toutes les entités de la simulation.
        """
        return self.__gui_bridge.simulator_request_entities()

    def add_stat(self, item):
        """
        Ajoute un item à la liste des statistiques/légendes.
        """
        self.__qml_bridge.add_stat(item)

    @Slot()
    def __stop(self):
        """
        Récupération du signal d'arrêt de la simulation et redirection sur
        le simulateur.
        """
        self.event_stop.set()
        self.__gui_bridge.simulator_play()
        self.__gui_bridge.simulator_stop()
        self._timer.stop()

    @Slot()
    def __play(self):
        """
        Récupération du signal de lancement de la simulation et redirection sur
        le simulateur.
        """
        self.__gui_bridge.simulator_play()

    @Slot()
    def __pause(self):
        """
        Récupération du signal de pause de la simulation et redirection sur
        le simulateur.
        """
        self.__gui_bridge.simulator_pause()

    @Slot()
    def _render_updated(self):
        """
        Averti l'interface que le rendu de la simulation est chargée.
        """
        self._frames = self._frames + 1
        self.event_render_updated.set()

    @Slot()
    def _update_framerate(self):
        """
        Mise à jour des images par secondes dans l'interface.
        """
        self._framerate.content = self._frames
        self._frames = 0

    def run(self):
        """
        Thread de contrôle et de gestion de l'interface graphique.
        """

        # Récuperation des informations de map et entités.
        self.__next_data = self.__gui_bridge.simulator_request_entities()
        self.__map_data = self.__gui_bridge.simulator_request_map()

        # Ajout des items de statistique à l'interface.
        for item in self.__gui_bridge.simulator_request_stats_items():
            self.add_stat(item)

        self.add_stat(self._framerate)

        # Démarrage du timer qui permet de compte le nombre d'images par
        # secondes.
        self._timer.start()

        while not self.event_stop.is_set():

            # Récupération des entités qui ont changé de place.
            self.__next_data = self.__gui_bridge.simulator_next()

            # Condition d'arrêt de la simulation.
            if self.__next_data is None:
                self.__qml_bridge.simulation_finished()
                self.__stop()

            # Mise à jour et attente de l'affichage du nouveau rendu.
            self.__qml_bridge.update_render()
            self.event_render_updated.wait()
