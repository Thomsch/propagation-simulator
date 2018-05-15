#!/usr/bin/env python
# -*-coding:utf-8-*-

""" Lit un fichier de configuration *.json contenant une
description des attributs d'une entité.
"""

from simerrors import *
from sim_parser import SimParser
import functools
from simutils import SimUtils

class AttrParser(SimParser):
    """ Lit et retourne un fichier contenant des attributs pour un
    type d'entité définit par l'utilisateur."""

    need_refresh = ("_x", "_y")
    overrides = ("_color", "_name",\
        "_plural_name", "_is_affected", "_labels")

    def __init__(self, entity_name):
        super(AttrParser, self).__init__(entity_name)
        default_color = SimUtils.randcolor((0,0,0))
        self.default_values = {"_x" : 0,\
                      "_y" : 0,\
                      "_is_affected" : False,\
                      "_color" :  default_color,\
                      "_name" : entity_name,\
                      "_plural_name" : entity_name + 's'}


    def _validate_attributes(self, attributes_json):
        for attribute_name, attribute_value in attributes_json.iteritems():
            self._validation_identifier(attribute_name, False, 1)
            if attribute_name[0] == '_' and \
                not (attribute_name in self.overrides or\
                    attribute_name in self.need_refresh):
                e = InvalidIdentifierError()
                e.add_message("Exception Message", "Attribute cannot be override")
                e.add_message("Attribute", attribute_name)
                e.add_message("Attribute Allowed", ", ".join(self.overrides))
                raise e

    def read_attributes(self):
        """ Lit et parse les attributs du fichier de configuration
        contenant les attributs. Vérifie le nom des attributs
        pour qu'ils soient des identificateur python valide.
        """
        init_filename = self._get_entity_filename("attributes.json")
        try:
            attributes = self._read_file(init_filename)
            attributes = dict(self.default_values, **attributes)

            self._validate_attributes(attributes)
            attributes_prop = dict()
            for key, value in attributes.items():
                attributes_prop[key] = self._create_property(key, value)

            if  '_labels' not in attributes :
                attributes_prop['_labels'] = self._create_property('_labels', {attributes['_name'] : attributes['_color']})

            return attributes_prop
        except ParserError as e:
            e.add_message("Action", "Reading attributes")
            raise e

    def _create_property(self, attribute_name, initial_value):
        """ Définit l'attribut donné comme une propriété.
        Une propriété est un ensemble de deux fonction get et set
        qui permet respectivement d'accéder et d'éditer à l'attribut.
        Etant donné que la métaclasse utilise le parseur, nous n'avons théoriquement
        pas accès aux instances crées. Cependant, nous pouvons définir un get qui
        crée l'attribut dans l'instance au moment du premier appel.
        Ainsi l'utilisation du dictionnaire est transparent pour les classes
        crées par la métaclasse.
        """
        def get(self, attr, initial_value):
            """ Retourne l'attribut, et l'insère dans le dictionnaire de
            l'instance si l'attribut n'existe pas """
            return self.__dict__.get(attr, initial_value)

        def erase(self, value, attr):
            """ Ecrase l'ancienne valeur aléatoirement
                (dans le cas de double modifications dans un pas de simulation) """
            erase = SimUtils.random().randint(0, 1) == 0
            if erase :
                self.__future__[attr] = value
            return erase

        def set_with_refresh(self, value, attr):
            """ dès que la propriété est modifié, nous
            appliquons la modification et nous mettons un
            fanion pour que la vue sache qu'il faut rafraichir l'entité """
            if attr in self.__future__:
                # cas d'écrasement avant un swap
                erase(self, value, attr)
            else:
                self.__future__[attr] = value
                self._need_refresh = True

        def set_without_refresh(self, value, attr):
            """ définit la modification de la propriété dans le tampon """
            if attr in self.__future__:
                erase(self, value, attr)
            else:
                self.__future__[attr] = value


        get = functools.partial(get,
                         attr=attribute_name,
                         initial_value=initial_value)

        if attribute_name in AttrParser.need_refresh:
            set = functools.partial(set_with_refresh,
                             attr=attribute_name)
        else:
            set = functools.partial(set_without_refresh,
                             attr=attribute_name)
        return property(get, set)
