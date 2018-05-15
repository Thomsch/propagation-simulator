# -*-encoding:utf8-*-
from PySide.QtDeclarative import QDeclarativeView
from PySide.QtCore import Signal

class QMLView(QDeclarativeView):
    '''
    Fenêtre qui surcharge l'événement de fermeture afin de réaliser un 
    traitement spécial lors de la fermeture de la fenêtre.
    '''

    def __init__(self):
        QDeclarativeView.__init__(self)
        
    def closeEvent(self, event):
        """
        Se déclenche lors de la fermeture de la fenêtre. Un signal est
        lancé pour avertir le programme que l'utilisateur souhaite arrêter
        la simulation.
        """
        QDeclarativeView.closeEvent(self, event)
        self.closing.emit()
        
    # Définition du signal.
    closing = Signal()
        
        
    