#!/usr/bin/env python
# -*-coding:utf-8-*-
class PropsimError(Exception):
    """ Désigne une erreur fatale de parsing des scripts utilisateur.
    """

    def __init__(self):
        self.messages = []
        self.label_size = 25

    def add_message(self, label, message):
        """ Ajoute une ligne de message à l'exception """
        if isinstance(message, Exception):
            message = repr(message)

        self.messages.append('{} : {}' \
            .format( \
                label.ljust(self.label_size), \
                message))

    def add_title(self, title, fillchar = ' '):
        self.messages.append('{}'.format(title).ljust(self.label_size, fillchar))

    def get_message(self):
        return self.__str__()

    def __str__ (self):
        return "\n# Parsing Error\n{}\n".format(\
            "\n".join(reversed(self.messages)))
