#!/usr/bin/env python
# -*-coding:utf-8-*-

from PySide.QtDeclarative import QDeclarativeImageProvider
from gui.render import Render

from simutils import SimUtils

class ImageProvider(QDeclarativeImageProvider):
    """ Cette classe fourni un objet de type QPixmap à l'interface QML.
    Cette classe ne s'occupe pas de créer l'image, Render s'en charge.
    """
    def __init__(self, gui_handler):
        """  Constructeur. Crée un objet de type Render.

            gui_handler : Gestionnaire graphique.
        """
        QDeclarativeImageProvider.__init__(self, QDeclarativeImageProvider.Pixmap)
        self.__generator = Render(gui_handler, SimUtils.get_map_bounds()[0],
                                  SimUtils.get_map_bounds()[1])

    def requestPixmap(self, id, size, requestedSize):
        """ Méthode de sortie sur le QML.

            id   : Permet depuis le QML de multiplexer le type d'image
                   que l'on souhaite obtenir.
            size : Taille.
            requestedSize : Taille requise.
        """
        self.__generator.update()
        return self.__generator.pixmap()
