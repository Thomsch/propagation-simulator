#!/usr/bin/env python
# -*-coding:utf-8-*-

from parser import *
from simerrors import *
from loader import terrain
from loader.terrain import Terrain
from sim_parser import SimParser
import os

class MapParser(SimParser):
    """ Génération de la carte personnalisée selon le fichier de config
    à voir => méthode 'read_configuration' """

    def __init__(self):
        super(MapParser, self).__init__("Terrain")
        self.special_areas = []
        self.default_terrain = None

    def __draw_pixel(self, a, b, terrain, function):
        """ voir __ellipse
        Dessin d'un pixel """
        function((a, b, terrain))
    
    def __ellipse_plot_points(self, xc,yc,  x,  y, terrain, function):
        """ voir __ellipse
        Génération des coordonnées pour chaque zone """
        self.__draw_pixel(xc + x, yc + y, terrain, function)
        self.__draw_pixel(xc - x, yc + y, terrain, function)
        self.__draw_pixel(xc + x, yc - y, terrain, function)
        self.__draw_pixel(xc - x, yc - y, terrain, function)
    
    def __ellipse(self, xc,yc,  a,  b, terrain, function):
        """ Création d'une ellipse avec des coordonnées cartésiennes
        Source de l'algo:
        http://stackoverflow.com/questions/15474122/
        is-there-a-midpoint-ellipse-algorithm, 30.12.2013"""
        a2 = a * a
        b2 = b * b
        twoa2 = 2 * a2
        twob2 = 2 * b2
        x = 0
        y = b
        px = 0
        py = twoa2 * y
    
        # Plot the initial point in each quadrant. */
        self.__ellipse_plot_points (xc,yc, x, y, terrain, function)
    
        # Region 1
        p = round (b2 - (a2 * b) + (0.25 * a2))
        while px < py:
            x += 1
            px += twob2
            if p < 0:
                p += b2 + px
            else:
                y -= 1
                py -= twoa2
                p += b2 + px - py
            self.__ellipse_plot_points (xc,yc, x, y, terrain, function)
    
        # Region 2
        p = round (b2 * (x+0.5) * (x+0.5) + a2 * (y-1) * (y-1) - a2 * b2)
        while y > 0:
            y -= 1
            py -= twoa2
            if p > 0:
                p += a2 - py
            else:
                x += 1
                px += twob2
                p += a2 - py + px
            self.__ellipse_plot_points (xc,yc, x, y, terrain, function)

    def read_configuration(self, file_system_path):
        """
        Définit le terrain pour des différentes zones configuré dans
        le fichier de config où le nom est passé par paramètre
        
        Arguments :
        file_system_path -- L'emplacement du fichier des config
        """

        try:
            map_json = self._read_file(file_system_path)
            for terrain_key, terrain_attributes in map_json.iteritems():
                
                if terrain_key == "default_terrain":
                    if terrain_attributes.keys()[0] == "terrain":
                        self.default_terrain = terrain_attributes.values()[0] 
                
                if terrain_key == "special_areas":
                    for special_area in terrain_attributes:
                        # déterminer le type
                        for attr in special_area.iteritems():
                            if attr[0] == "type":
                                type = attr[1]
                        # déterminer le terrain
                        for attr in special_area.iteritems():
                            if attr[0] == "terrain":
                                terrain = attr[1]
                        # déterminer les dimensions
                        for attr in special_area.iteritems():
                            if attr[0] == "dimensions":
                                x = attr[1][0]
                                y = attr[1][1]
                                width = attr[1][2]
                                height = attr[1][3]
                                
                        if type == "Rectangle":
                            for i in xrange(width):
                                for j in xrange(height):
                                    self.special_areas.append((x+i, y+j, terrain))
                        
                        if type == "Ellipse":
                            for i in range(width):
                                for j in range(height):
                                    self.__ellipse(x, y, i, j, terrain, self.special_areas.append)
                        
        except ParserError as e:
            e.add_message("Action", "Reading terrains")
            raise e