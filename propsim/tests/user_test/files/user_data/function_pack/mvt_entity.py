# -*- coding: utf8 -*-
from simutils import *
import math

class MvtEntity(Trigger):
    """ Contient en clé la classe de l'entity, et en valeur le booléen si
    l'entité à bien été checkée """
    is_checked = dict()
    theta = math.radians(2)

    @staticmethod
    def man_page():
        """ Affiche le manuel utilisateur de MvtEntity """
        print "mvt_entity manual".center(90, "-")
        print "This trigger is to move an entity in a direction with a variable speed."
        print "Each iteration, the speed change according an array speed_progress. The"
        print "speed adopted is defined by the index speed_id, which represents the index"
        print "of speed progress array\n"
        print "mvt_entity example".center(90, ".")
        print "In file attributes.json"
        print "{"
        print "\"direction\" : [0, 1],"
        print "\"speed_progress\" : [3, 1, 1, 1, 1, 2, 2],"
        print "\"speed_id\" : 0"
        print "}\n"
        print "In file action.json"
        print "{"
        print "\"normal_move\": {"
        print "\"with\" : [\"Earth\", \"Mountain\"],"
        print "\"action\" : \"/functions_pack/mvt_humain\""
        print "}"
        print "".center(90, "-")

    @classmethod
    def is_performed(cls, data):
        """ L'action est toujours appelée.
        Test si les attributs nécessaires aux Trigger existent
        bien
        """
        if not cls.is_checked.has_key(type(data.entity1)):
            try:
                speed_id = data.entity1.speed_id
            except Exception as e:
                print "Entity ", data.entity1.__name__,\
                    " need attribute speed_id in ", self.__name__
                cls.man_page()
                exit(1)

            try:
                speed_progress = data.entity1.speed_progress
            except Exception as e:
                print "Entity ", data.entity1.__name__,\
                    " need attribute speed_progress in ", self.__name__
                cls.man_page()
                exit(1)

            try:
                direction = data.entity1.direction
            except Exception as e:
                print "Entity ", data.entity1.__name__,\
                    " need attribute direction in ", self.__name__
                cls.man_page()
                exit(1)

            cls.is_checked[type(data.entity1)] = True
        return True

    @classmethod
    def action_performed(cls, data):
        """ Déplacer l'entité sur la carte selon un pas
        humanoïde cohérent
        """
        x = data.entity1._x
        y = data.entity1._y
        terrains = SimUtils.get_terrain_names()
        speed_progress = data.entity1.speed_progress

        speed = speed_progress[data.entity1.speed_id]
        (vecx, vecy) = data.entity1.direction
        try_count = 1
        next_x = 0
        next_y = 0
        theta = cls.theta

        while True:
            # Ajout de variation dans le mouvement
            theta = theta + math.radians(SimUtils.random().randint(-1, 1))
            next_x = math.floor(speed * vecx) + x
            next_y = math.floor(speed * vecy) + y
            in_map = SimUtils.is_in_map_area(next_x, next_y)
            if in_map and\
               str(terrains[SimUtils.get_terrain_type(next_x, next_y)]) in (data.terrains) :
                break
            elif not in_map:
                (vecx, vecy) = (-vecx, -vecy)

            cs = math.cos(theta)
            sn = math.sin(theta)
            vecx = vecx * cs - vecy * sn
            vecy = vecx * sn + vecy * cs

            if vecx == 0 and vecy == 0:
                vecx = SimUtils.random().randint(-speed, speed)
                vecy = SimUtils.random().randint(-speed, speed)
            try_count += 1

        data.entity1.direction = (vecx, vecy)
        data.entity1.speed_id = (data.entity1.speed_id + 1) % len(speed_progress)
        data.entity1._move_entity(next_x, next_y)
