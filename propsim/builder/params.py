#!/usr/bin/env python
# -*-encoding:utf8-*-
from simutils import *

class Params(object):
    """Temporaire pour contenir le minium vital du simulateur."""

    def __init__(self, iterations, display_enable, entity_class, entity_colors, entities,
                 sim_map, map_size, min_delay_between_refreshes,
                 nb_iterations_before_refresh, interactions, interaction_range,
                 seed, seed_map):
        """ Nombre d'itération à réaliser pour la simulation """
        self.iterations = iterations
        """ Si la simulation demande un affichage """
        self.display_enable = display_enable

        """ Liste de toutes les classes d'entités """
        self.entity_class = entity_class
        """ Liste de couleur pour chacune des listes de entity_class """
        self.entity_colors = entity_colors
        """ Toutes les instances d'entités """
        self.entities = entities

        """ cls.Le délai de raifrichissement """
        self.min_delay_between_refreshes = min_delay_between_refreshes
        """ Carte de la simulation """
        self.sim_map = sim_map
        """ Dimension de la carte (largeur, hauteur) """
        self.map_size = map_size
        """ Rafraîchissement tout les quantum pas """
        self.nb_iterations_before_refresh = nb_iterations_before_refresh
        """ Instance permettant d'appeler toutes les interactions de la simulation """
        self.interactions = interactions
        """ Le rayon des interactions """
        self.interaction_range = interaction_range

        """ Les différents valeurs pour initialisés les générateurs aléatoires """
        self.seed = seed
        self.seed_map = seed_map

    def log(self):
        # Ecriture du fichier d'export contenant les données de la simulation courante
        start_log = { "num.iterations" : self.iterations,
        "map.width" : self.map_size[0], "map.height" : self.map_size[1],
        "num.entity" : len(self.entities), "sim.seed" : self.seed if self.seed is not None else "None",
        "map.seed" : self.seed_map if self.seed_map is not None else "None", "interaction.range" : self.interaction_range};
        for entity in self.entity_class :
            inst = entity()
            label = "entity.{}".format(entity.__name__)
            start_log[label+".name"] = inst._name
            start_log[label+".plural_name"] = inst._plural_name
            start_log[label+".color"] = inst._color
            start_log[label+".count"] = len([e for e in self.entities if e.__name__ == entity.__name__])

        SimUtils.write_in_file("Parameters", start_log)

    def __str__(self):
        """ Retourne tous les attributs disponibles"""
        sb = []
        sb.append("PARAMS".ljust(50, "="))
        for key, value in self.__dict__.iteritems():
            if key is not "entities":
                sb.append("{:<20}  : {:<20}".format(key, value))
            else:
                sb.append("{:<20}  : {:<20} (count)".format(key, len(value)))
        return "\n".join(sb)
