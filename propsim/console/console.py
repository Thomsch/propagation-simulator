#!/usr/bin/env python
# -*-coding:utf-8-*-

from PySide.QtGui import QPlainTextEdit
from PySide.QtGui import QIcon
from PySide.QtCore import Signal, Slot
import os

WINDOW_ICO_PATH = os.path.join("simutils", "icon_256x256.png")

class Console (QPlainTextEdit):

    """
    Classe permettant d'afficher des informations dans diverses couleurs selon
    leur type.
    """

    info = "INFO - "
    warning = "WARNING - "

    def __init__(self, title):
        """
        Constructeur.
        Paramétrisation de la console.
        """
        QPlainTextEdit.__init__(self)
        self.setWindowTitle(str(title))
        self.setWindowIcon(QIcon(WINDOW_ICO_PATH))
        self.setReadOnly(True)
        self.show_request.connect(self.show_listener)
        
    def show(self):
        """
        Redéfinition de la méthode show() afin que des thread externes à Qt
        puissent invoquer cette méthode.
        """
        self.show_request.emit()
        
    @Slot()
    def show_listener(self):
        """
        Affiche la fenêtre lorsque le signal show_request est lancé.
        """
        super(Console, self).show()

    def push(self, string):
        """
        Permet d'ajouter du texte à la console sous le label info.
        """
        self.appendPlainText(Console.info + string)

    def push_error(self, string):
        """
        Permet d'ajouter du texte à la console sous le label error.
        """
        self.appendHtml("<font color=\"red\">" + string + "</font>")

    def push_warning(self, string):
        """
        Permet d'ajouter du texte à la console sous le label warning.
        """
        self.appendHtml("<font color=\"orange\">" + Console.warning + string + "</font>")
        
    # Permet de faire la liaison entre le thread externe à Qt qui appel Show()
    # et la méthode véritable qui l'éxecute.
    show_request = Signal()