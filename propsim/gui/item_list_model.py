#!/usr/bin/env python
# -*-encoding:utf8-*-

from PySide.QtCore import QAbstractListModel, QModelIndex, Slot
from PySide.QtGui import QColor
from PySide import QtCore

class ItemListModel(QAbstractListModel):
    """
    Modèle de liste pour l'affichage des items de statistiques sur l'interface
    graphique.
    """
    roles = ('item','color','hasColor')
    def __init__(self, items):
        QAbstractListModel.__init__(self)
        self._items = items
        self.setRoleNames(dict(enumerate(self.roles)))

    def rowCount(self, parent=QModelIndex()):
        """
        Renvoie le nombre de lignes.
        """
        return len(self._items)

    def data(self, index, role):
        """
        Renvoie le contenu de l'item situé à index. Le rôle permet de
        determiner si l'item est editable ou autre.
        """
        if index.isValid():
            if role == self.roles.index('item'):
                return self._items[index.row()].name() + str(self._items[index.row()].content)
            elif role == self.roles.index('color'):
                return self._items[index.row()].color()
            elif role == self.roles.index('hasColor'):
                return self._items[index.row()].color() != None
        return "Wrong item"

    def add_item(self, item):  
        """
        Ajout un item à la liste et préviens le modèle quand il change.
        """ 
        self.beginInsertRows(QModelIndex(), len(self._items), len(self._items))
        self._items.append(item)    
        self.endInsertRows()
        item.changed.connect(self.itemChanged)
        
    @Slot()
    def itemChanged(self):
        """
        Se déclenche dès que le contenu d'un item est changé.
        """
        self.modelReset.emit()
        # Voir setItemData.