# -*-coding:utf-8-*-
import threading, time
from PySide.QtCore import Signal
from PySide.QtCore import QObject

class Timer(QObject, threading.Thread):
    '''
    Mesure le temps toutes les x secondes. A chaque x secondes, le signal
    on_action est émit.
    '''
    def __init__(self, seconds):
        '''
        Constructeur.
            - seconds : Nombre de secondes après lesquelles un signal est
                        lancé.
        '''
        threading.Thread.__init__(self)
        QObject.__init__(self)
        
        self._running = seconds > 0.0
        self._delay = seconds
        
    def stop(self):
        """
        Stoppe le timer sans la possibilité de le redémarrer.
        """
        self._running = False   
        
    def run(self):
        """
        Boucle d'exécution du thread du comptage de secondes.
        """
        while(self._running):
            time.sleep(self._delay)
            self.on_action.emit()

    on_action = Signal()