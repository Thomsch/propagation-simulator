#!/usr/bin/env python
# -*-coding:utf-8-*-

from PySide.QtGui import QPixmap, QColor, QImage
from simutils.sim_utils import SimUtils
from data.stat_item import StatItem

from operator import attrgetter

class Render(object):
    '''
    Cette classe génère une image lorsqu'une instance de la classe
    image_provider demande une mise à jour.
    '''

    def __init__(self, gui_handler, width, height):
        '''
        Constructeur
        '''
        self.__gui_handler = gui_handler
        self.__width = width
        self.__height = height

        self.__pixmap = QPixmap(self.__width, self.__height)
        self.__image = QImage(self.__width, self.__height, QImage.Format.Format_RGB32)

        self.positions = {}

        # Pour savoir si c'est le premier tour ou pas.
        self.__first = True

        # Contient les différents types d'entités et terrain avec leurs
        # couleurs associées.
        self.__terrain = []

    def pixmap(self):
        """
        Renvoie le pixmap mis à jour.
        """
        self.__pixmap = QPixmap.fromImage(self.__image)
        return self.__pixmap

    def update(self):
        """"
        Mise a jour de l'image.
        """
        if self.__first:
            self.__first = False
            self.__map_data = self.__gui_handler.get_map_data()
            self.__next_data = self.__gui_handler.get_entities()
            labels = []

            # Découverte du terrain
            for terrain in SimUtils.get_terrains():
                self.__terrain.append(terrain.color)
                labels.append(StatItem(terrain.name, "", terrain.color))

            # Tri lexicographique des labels.
            labels.sort(key=lambda stat: stat._name)
            # Ajout des labels de terrain
            for label in labels:
                self.__gui_handler.add_stat(label)

            # Remplissage de la carte avec les terrains.
            for i in range(0, self.__width):
                for j in range(0, self.__height):
                    # Affichage du point.
                    color = QColor(self.__terrain[self.__map_data.get_terrain_type(i,j)])
                    self.__image.setPixel(i,j,color.rgb())

            # Permet de faire le tri entre les entités déjà rencontrées et les
            # autres.
            entity_types = {}

            # Liste des futurs labels
            labels = []

            # Découverte des entités - affectation des couleurs
            for entity in self.__next_data:
                # Ajout des labels de couleur pour les entités
                if not entity_types.has_key(entity.__name__):
                    entity_types[entity.__name__] = True

                    for label, color in entity._labels.iteritems():
                        labels.append(StatItem(label, "", color))

                # Affichage de l'entité.
                self.__image.setPixel(entity._x, entity._y, QColor(entity._color).rgb())
                self.positions[id(entity)] = [entity._x, entity._y]

            # Tri lexicographique des labels.
            labels.sort(key=lambda stat: stat._name)

            for label in labels:
                self.__gui_handler.add_stat(label)
        else:
            # Mise à jour du rendu
            for entity in self.__next_data:
                # Cas d'une entité désactivée (morte)
                remove_entity = not entity._is_active()
                if id(entity) not in self.positions:
                    # Ajout de l'entité en cours de simulation
                    self.__image.setPixel(entity._x, entity._y, QColor(entity._color).rgb())
                    self.positions[id(entity)] = [entity._x,entity._y]

                # Le simulateur demande de repeindre l'entité
                old_points = self.positions[id(entity)]

                if not remove_entity:
                    self.positions[id(entity)] = [entity._x, entity._y]

                # On remet la couleur du terrain.
                color = QColor(self.__terrain[self.__map_data.get_terrain_type(old_points[0], old_points[1])])
                self.__image.setPixel(old_points[0], old_points[1], color.rgb())

                if not remove_entity:
                    # Ajout des paramètres de setPixel dans une liste pour être ploté après.
                    self.__image.setPixel(entity._x, entity._y, QColor(entity._color).rgb())
