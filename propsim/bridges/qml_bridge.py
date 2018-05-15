#!/usr/bin/env python
# -*-encoding:utf8-*-

from gui.item_list_model import ItemListModel
from PySide.QtCore import QObject, Slot, Signal, Property

# Nom du fichier de la vue qml.
SOURCE = "./gui/qml/view.qml"

# Nom du controleur pour le QML.
CONTROLLER_NAME = "controller"

# Nom du controleur pour le modèle de liste des statisques.
STATS_NAME = "stats"

class QMLBridge(QObject):
    """
    Classe de liaison entre l'interface en QML et le gestionnaire de l'interface en Python.
    """
    def __init__ (self, view, stats):
        """
        Constructeur.
        Paramétrisation des liaisons pour le QML.
        """
        QObject.__init__(self)
         
        self._model = ItemListModel(stats)
        
        self._running = False
        self._stopped = False
        
        root_context = view.rootContext()
        root_context.setContextProperty(CONTROLLER_NAME, self)
        root_context.setContextProperty(STATS_NAME, self._model)
        
        view.setSource(SOURCE)
        root_object = view.rootObject()
        
        self._render = root_object.findChild(QObject, "render")
        self._render.render_updated.connect(self.render_updated)
        self.on_render_update.connect(self._render.updateRender)
        
    def add_stat(self, item):
        """
        Ajoute des statistiques au modèle.
        item : Statistique à ajouter.
        """
        self._model.add_item(item)

    def update_render(self):
        """
        Demande à l'interface de mettre à jour le rendu de la simulation.
        """
        self.on_render_update.emit()

    @Slot()
    def render_updated(self):
        """
        Méthode appelée lorsque le rendu de simulation a fini d'être affiché.
        """
        self.on_render_updated.emit()
    
    @Slot()
    def start_simulation(self):
        """
        Méthode appelée lorsque l'utilisateur appuie sur le bouton start.
        """
        self._set_running(True)
        self.on_played.emit()
        
    @Slot()
    def pause_simulation(self):
        """
        Méthode appelée lorsque l'utilisateur appuie sur le bouton pause.
        """
        self._set_running(False)
        self.on_paused.emit()
      
    @Slot()  
    def stop_simulation(self):
        """
        Méthode appelée lorsque l'utilisateur appuie sur le bouton stop.
        """
        self._set_running(False)
        self._set_stopped(True)
    
    def simulation_finished(self):
        """
        Méthode appelée lorsque la simulation est terminée.
        """
        self._set_running(False)
        self._set_stopped(True)
        
    def _get_running(self):
        """
        Accesseur de la variable _running.
        """
        return self._running
 
    def _set_running(self, running):
        """
        Setteur de la variable _running.
        """
        self._running = running
        self.on_running.emit()  

    def _get_stopped(self):
        """
        Accesseur de la variable _stopped.
        """
        return self._stopped
 
    def _set_stopped(self, stopped):
        """
        Setteur de la variable _stopped.
        """
        self._stopped = stopped
        self.on_stopped.emit()

    """
    Définition des signaux qui assure la communication entre le QML et le Python.
    """
    # Gestion de l'état de la simulation.
    on_running = Signal()
    on_stopped = Signal()
    on_paused = Signal()
    on_played = Signal()
    
    # Mise à jour du rendu graphique.
    on_render_updated = Signal()
    on_render_update = Signal()
    
    # Definition des propriétés.
    running = Property(bool, _get_running, _set_running, notify=on_running) 
    stopped = Property(bool, _get_stopped, _set_stopped, notify=on_stopped)