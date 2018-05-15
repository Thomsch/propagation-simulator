#!/usr/bin/env python
# -*-coding:utf-8-*-

class Controls(object):
    """ Les contrôles du simulateur """
    
    def __init__(self):
        pass

    def play(self):
        """Demande à la cible de démarrer son traitement."""
        raise NotImplementedError( "Simulator : play" )

    def pause(self):
        """Demande à la cible de mettre en pause son traitement."""
        raise NotImplementedError( "Simulator : pause" )
    
    def stop(self):
        """Demande à la cible de cesser définitivement son traitement."""
        raise NotImplementedError( "Simulator : stop" )