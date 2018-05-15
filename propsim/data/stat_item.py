#!/usr/bin/env python
# -*-encoding:utf8-*-

from PySide.QtCore import QObject, Signal, Property

class StatItem(QObject):  
    """
    Item de statistique sur le déroulement du programme qui sera affiché 
    dans l'interface sur le paneau de droite.
    """
    def __init__(self, name, content, color = None):
        QObject.__init__(self)
        self._content = content
        self._name = name
        self._color = color

    def _content(self):
        return self._content
    
    def name(self):
        return self._name
    
    def color(self):
        return self._color
    
    def _set(self, content):
        self._content = content
        self.changed.emit()

    changed = Signal()
    content = Property(unicode, _content, _set, notify=changed)