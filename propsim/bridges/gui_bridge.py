#!/usr/bin/env python
# -*-coding:utf-8-*-

import threading

class GUIBridge(object):
    """ Connecteur simulateur-gui. Les méthodes préfixées par
    "simulator" effectuent des demandes au simulateur, celle préfixées
    par "gui" font des requêtes au gestionnaire d'interface.
    """

    def __init__(self):
        self.event_next = threading.Event()
        self.event_done = threading.Event()

        # Event pour s'assurer la mise en attente en cas d'appel prématuré d'une
        # fonction.
        self.event_simulator_registered = threading.Event()
        self.event_gui_registered = threading.Event()
        self.simulator_registered = False
        self.gui_registered = False

    def register_gui(self, gui):
        """ Enregistre l'interface graphique auprès de la passerelle. Ne
        fait rien si un enregistrement a déjà eu lieu. """
        self.__dict__.setdefault("gui", gui)
        self.gui_registered = True
        self.event_gui_registered.set()

    def register_simulator(self, simulator):
        """ Enregistre le simulateur auprès de la passerelle. Ne fait
        rien si un enregistrement a déjà eu lieu. """
        self.__dict__.setdefault("simulator", simulator)
        self.simulator_registered = True
        self.event_simulator_registered.set()

    def simulator_play(self):
        """ Indique au simulateur de démarrer. """
        if not self.simulator_registered:
            self.event_simulator_registered.wait()
        self.simulator.play()

    def simulator_pause(self):
        """ Indique au simulateur de se mettre en pause. """
        if not self.simulator_registered:
            self.event_simulator_registered.wait()
        self.simulator.pause()

    def simulator_stop(self):
        """ Indique au simulateur de cesser toute activité. """
        if not self.simulator_registered:
            self.event_simulator_registered.wait()
        self.simulator.stop()
        # S'assure que le simulateur et l'interface soient débloqués pour
        # terminer correctement.
        self.event_next.set()
        self.event_next.set()

    def simulator_next(self):
        """ Indique au simulateur de passer à l'itération suivante.
        Retourne les entités ayant été modifiées depuis la dernière
        itération, ou None s'il la simulation est terminée. """
        if not self.simulator_registered:
            self.event_simulator_registered.wait()
        if not self.simulator.is_achieved() and not self.simulator.is_stopped():
            self.event_next.set()
            self.event_done.wait()
            self.event_done.clear()
            return self.simulator.request_entities_updated()
        else:
            return None

    def simulator_request_stats_items(self):
        """ Retourne les éléments caractéristiques de la simulation. """
        if not self.simulator_registered:
            self.event_simulator_registered.wait()
        return self.simulator.request_stats_items()

    def simulator_request_map(self):
        """ Retourne la carte de la simulation. """
        if not self.simulator_registered:
            self.event_simulator_registered.wait()
        return self.simulator.request_map()

    def simulator_request_entities(self):
        """ Retourne toutes les entités de la simulation. """
        if not self.simulator_registered:
            self.event_simulator_registered.wait()
        return self.simulator.request_entities()

    def gui_print_ready(self):
        """ Indique à l'interface graphique (gestionnaire) qu'il peut
        afficher la nouvelle itération. """
        if self.gui_registered:
            self.event_done.set()
            self.event_next.wait()
            self.event_next.clear()

