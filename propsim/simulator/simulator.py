#!/usr/bin/env python
# -*-coding:utf-8-*-

from __future__ import division
import threading
import time
from math import ceil, sqrt

from controls import Controls
from data.stat_item import StatItem
from simutils.sim_utils import SimUtils
from console.console import Console

# Pour la gestion des exceptions
import sys, traceback
from simerrors.propsim_error import PropsimError
from config.globals import Globals

from sim_export import *

class Simulator(threading.Thread, Controls):
    """ Le simulateur gérant le déroulement et les contrôles. """

    def __init__(self, gui_bridge, params):
        threading.Thread.__init__(self)
        self.gui_bridge = gui_bridge
        self.params = params
        self.event_start = threading.Event()
        self.event_pause = threading.Event()
        self.event_stop = threading.Event()
        self.entities_updated = {}
        self.console = Console("Error")

        # StatItems
        self.current_iteration = StatItem("Iteration: ", 0)

        # Liste des entités à ajouter & supprimer
        self.entities_to_remove = []
        self.entities_to_add = []
        # Zones de la carte pour rayon d'interactions et positions
        self.areas = []
        self.area_interaction_range_min = 1 # valeur de détection minimale pour les calculs de zone
        self.area_square_size = 0
        self.area_number_height = 0
        self.area_number_width = 0


    def play(self):
        """ Démarre le simulateur. """
        self.event_start.set()

    def pause(self):
        """ Met la simulation en pause. """
        self.event_pause.set()

    def stop(self):
        """ Termine la simulation. """
        self.event_stop.set()

    def is_stopped(self):
        """ Retourne si la simulation a été stoppée ou non. """
        return self.event_stop.is_set()

    def is_achieved(self):
        """ Retourne si la simulation s'est terminée ou non. """
        return self.current_iteration.content == self.params.iterations

    def request_stats_items(self):
        """ Retourne les statistiques définies sous forme de liste de StatItem. """
        stats = list()
        # Itération courante
        stats.append(self.current_iteration)

        return stats

    def get_current_iteration(self):
        """ Retourne le numéro de l'itération courante. """
        return self.current_iteration.content

    def request_map(self):
        """ Retourne la carte de la simulation. """
        return self.params.sim_map

    def request_entities(self):
        """ Retourne les entités de la simulation. """
        return list(self.params.entities)

    def request_entities_updated(self):
        """ Retourne un dictionnaire des entités mises à jour lors de la
        dernière itération. Retourne None si le simulateur a été stoppé.
        """

        # Particularités:
        # - Pour la première itération, c'est le premier affichage, la
        #   totalité des entités est donc envoyée.
        # - Renvoi None si stoppé pour conserver un état cohérent de
        #   l'itération affichée.
        if self.is_stopped():
            return None
        elif self.current_iteration.content == 0:
            return self.request_entities()
        else:
            return self.entities_updated

    def remove_entity(self, entity):
        """ Ajoute l'entité donnée à la liste des entités qui seront
        supprimées à la fin de l'itération."""
        if entity not in self.entities_to_remove:
            self.entities_to_remove.append(entity)

    def add_entity(self, entity):
        """ Ajoute l'entité donnée à la liste des entités qui seront
        ajoutée à la fin de l'itération."""
        if entity not in self.entities_to_add:
            self.entities_to_add.append(entity)

    def get_entities(self, pos_x, pos_y):
        """ Retourne un set des entités à la position donnée si elle
        existe. Retourne None si la position n'est pas sur la carte.
        """
        if SimUtils.is_in_map_area(pos_x, pos_y):
            entities = set()
            area = self.areas[int(pos_y // self.area_square_size)]\
                             [int(pos_x // self.area_square_size)]
            for entity in area:
                if entity._x == pos_x and entity._y == pos_y:
                    entities.add(entity)
            return entities
        else:
            return None

    def run(self):
        """ Tâche principale, exécutée lors du démarrage du Thread. """

        # Tâches générales
        SimUtils._register_simulator(self)
        SimExport._register_get_iteration(self.get_current_iteration)
        self.params.log()
        # Initialisation des entités, avec les SimUtils
        for entity in self.params.entities:
            entity._init_entity()
            entity._swap()

        # Démarrage du mode graphique ou non
        try:
            if self.params.display_enable:
                if self.gui_bridge is not None:
                    self.gui_bridge.register_simulator(self)
                    self.__display_mode()
                else:
                    raise AttributeError("Trying to start simulator in display mode without GUIBridge.")
            else:
                self.__stealth_mode()
        except PropsimError as e:
            self.stop()
            if self.params.display_enable:
                self.gui_bridge.gui_print_ready()

            exc_type, exc_value, exc_traceback = sys.exc_info()
            print exc_type.__name__.center(90, '-')
            print traceback.format_exc().splitlines()[-1]
            print "".ljust(90, '.')
            traceback.print_exception(exc_type,
                exc_value, exc_traceback, file=sys.stdout)
            print "".ljust(90, '-')

            self.console.show()
            self.console.push_error("Error executing simulation {}".format(Globals._simulation_name))
            for message in reversed(e.messages):
                self.console.push_error(message)

    def __wait_start(self):
        """ Attend la réception d'un signal start. """
        self.event_start.wait()
        self.event_start.clear()
        self.event_pause.clear()

    def __check_pause(self):
        """ Vérifie si le simulateur a été mis en pause ou non. Attend
        la reprise en cas de pause.
        """
        if self.event_pause.is_set():
            self.__wait_start()

    def __apply_remove_list(self):
        """ Supprime de la liste d'entités toutes celles contenues dans
        la liste de suppression en attente.
        """
        for entity in self.entities_to_remove:
            entity._set_active(False)
            # Ajout de l'entité dans la liste des mises à jours
            self.entities_updated.setdefault(id(entity), entity)

        # Vide la liste
        self.entities_to_remove = []

    def __apply_add_list(self):
        """ Ajoute la liste d'entités à la simulation """
        for entity in self.entities_to_add:
            self.params.entities.add(entity)
            # Ajout de l'entité dans la liste des mises à jours
            entity._swap()
            self.entities_updated.setdefault(id(entity), entity)

        # Vide la liste
        self.entities_to_add = []

    def __assign_and_refresh_entities_to_areas(self):
        """ Assigne à une zone chaque entité pour accélérer le traitement.
        ATTENTION : à effectuer au début de chaque itération !
        """

        # Récupère la carte
        map_width = self.params.sim_map.width
        map_height = self.params.sim_map.height

        # Côté d'une petite zone
        if self.params.interaction_range < self.area_interaction_range_min:
            self.area_square_size = float(self.area_interaction_range_min * 2 + 1)
        else:
            self.area_square_size = float(self.params.interaction_range * 2 + 1)

        # Nombre de petites zones
        self.area_number_width = int(ceil(map_width / self.area_square_size))
        self.area_number_height = int(ceil(map_height / self.area_square_size))

        # Initialisation de la grille de zones
        self.areas = []
        for row in xrange(self.area_number_height):
            self.areas.append([])
            for _ in xrange(self.area_number_width):
                (self.areas[row]).append([])

        # Affectations des entités dans les zones ou suppression si entité inactive
        inactive_entities = []
        for entity in self.params.entities:
            if entity._is_active():
                area = self.areas[int(entity._y // self.area_square_size)]\
                                 [int(entity._x // self.area_square_size)]
                area.append(entity)
            else:
                inactive_entities.append(entity)
        for entity in inactive_entities:
            self.params.entities.remove(entity)

    def __compute_interactions(self):
        """ Détermine les interactions à réaliser et les applique. """

        # Création des interactions pour chaque zone selon ses voisines
        for row in xrange(self.area_number_height):
            for col in xrange(self.area_number_width):
                entities = self.areas[row][col]
                number = len(entities)

                # Ajout de la zone à droite
                if self.params.interaction_range >= self.area_interaction_range_min \
                   and col < self.area_number_width - 1:
                    entities.extend(self.areas[row][col+1])

                # Ajout de la ligne du bas
                if self.params.interaction_range >= self.area_interaction_range_min \
                   and row < self.area_number_height - 1:
                    # Zone bas-gauche
                    if col > 0:
                        entities.extend(self.areas[row+1][col-1])
                    # Zone bas-centre
                    entities.extend(self.areas[row+1][col])
                    # Zone bas-droite
                    if col < self.area_number_width - 1:
                        entities.extend(self.areas[row+1][col+1])

                for i in xrange(number):
                    count = 0
                    current = entities[i]

                    # Remarques sur le traitement à venir :
                    # 1. Ignore les entités venant avant dans la liste
                    #    (permet d'éviter les doublons du genre :
                    #    (e1,e3) et (e3,e1)).
                    # 2. Une entité située dans le coin supérieur gauche
                    #    ou au milieu de la zone est forcément trop loin
                    #    des entités des zones adjacentes => ne comparer
                    #    qu'avec la même zone.
                    middle_position = self.area_square_size / 2
                    short_circuit = current._x % self.area_square_size <= middle_position \
                                    and current._y % self.area_square_size <= middle_position

                    for entity in entities:
                        if short_circuit and count >= number: # Assure le point 2
                            break
                        elif count > i: # Assure le point 1.
                            diff_x = current._x - entity._x
                            diff_y = current._y - entity._y
                            distance = round(sqrt(diff_x * diff_x + diff_y * diff_y),0)

                            if distance <= self.params.interaction_range:
                                self.params.interactions.apply_interactions(current, entity)

                        count += 1

    def __compute_next_iteration_stealth(self):
        """ Effectue les actions nécessaires à la préparation de l'état
        suivant.

        Fonctionne spécialement pour le mode sans affichage (ne test pas
        la pause).
        """

        # Initialisation des zones
        self.__assign_and_refresh_entities_to_areas()

        # Applique les actions
        for entity in self.params.entities:
            entity._apply_actions(self.params.sim_map.get_terrain_type(entity._x, entity._y))
            # export de l'entité, imprime son état en début d'itération (avant le _swap donc)
            entity._export()

        # Applique les interactions
        self.__compute_interactions()

        # Suppression des entités si demandé
        self.__apply_remove_list()
        self.__apply_add_list()

    def __compute_next_iteration_display(self):
        """Effectue les actions nécessaires à la préparation de l'état
        suivant.

        Fonctionne spécialement pour le mode graphique (test la pause).
        """

        # Initialisation des zones
        self.__assign_and_refresh_entities_to_areas()

        # Applique les actions
        for entity in self.params.entities:
            if self.event_stop.is_set():
                return
            self.__check_pause()

            entity._apply_actions(self.params.sim_map.get_terrain_type(entity._x, entity._y))
            # export de l'entité, imprime son état en début d'itération (avant le _swap donc)
            entity._export()

        # Applique les interactions
        self.__compute_interactions()

        # Suppression des entités si demandé
        self.__apply_remove_list()
        self.__apply_add_list()

    def __update_state(self):
        """Passe à l'état suivant."""

        if self.params.display_enable:
            for entity in self.params.entities:
                self.__check_pause()
                if entity._swap() or not entity._is_active():
                    self.entities_updated.setdefault(id(entity), entity) # ajoute que si nouveau
        else:
            for entity in self.params.entities:
                entity._swap()

        self.current_iteration.content = self.current_iteration.content + 1

    def __display_mode(self):
        """Tâche principale en cas de mode graphique."""

        # Pour l'affichage de l'état initial
        self.gui_bridge.gui_print_ready()

        self.__wait_start()

        display_time = False
        while not self.is_stopped() \
            and self.current_iteration.content < self.params.iterations:

            # Nécessaire pour que ça corresponde à l'itération courante
            # et non future (l'appel à "__update_state()" doit
            # incrémenter le compteur
            display_time = \
               self.current_iteration.content % self.params.nb_iterations_before_refresh == 0 \
               or self.current_iteration.content == self.params.iterations

            self.__compute_next_iteration_display()
            self.__update_state()

            if display_time:
                # Et prévoir gestion du taux d'affichage dans la partie
                # graphique
                time.sleep(self.params.min_delay_between_refreshes)
                self.gui_bridge.gui_print_ready()
                # Remise à zéro des entités ayant changé.
                self.entities_updated = {}

        # Nécessaire pour terminer le handshake de fermeture du combo
        # interface + simulateur
        self.gui_bridge.gui_print_ready()

    def __stealth_mode(self):
        """Tâche principale en cas de mode sans affichage."""

        while self.current_iteration.content < self.params.iterations:
            self.__compute_next_iteration_stealth()
            self.__update_state()
