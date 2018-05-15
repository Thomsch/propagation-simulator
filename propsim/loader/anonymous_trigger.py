#!/usr/bin/env python
# -*-coding:utf-8
""" Permet d'instancier un nouveau Trigger à partir
des deux fonction is_performed et action_performed données.
Des paramètres leurs sont respectivement donnés, qui seront
réevaluer à chaque appel du trigger.

Nous arrivons par ce biais à posséder une structure assez légère,
car tous les appels de fonctions sont statiques. Une action dans une
entité n'existera donc que sous une seule instance pour toutes les instances
d'entités.
Afin de gérer les modifications du containeur data (contient l'entité concernée par le Trigger etc.)
nous créeons une fonction anonyme lors du parsing qui se chargera avant l'appel de redéfinir se
paquet data.
(voir loader.parser.action_parser.__read_user_action.launch_action)
"""
from simutils import *
import inspect
import sys, traceback

def new_trigger(action_name, is_performed_func, is_performed_param, \
    action_performed_func, action_performed_param) :
    """ Crée un nouveau trigger d'après les deux fonctions données.
    """
    class AnonymousTrigger(Trigger):
        is_performed_func = None
        is_performed_param = None
        action_performed_func = None
        action_performed_param = None
        @classmethod
        def _define_functions(cls,is_performed_func, is_performed_param, \
            action_performed_func, action_performed_param):
            cls.is_performed_func = is_performed_func
            cls.is_performed_param = is_performed_param
            cls.action_performed_func = action_performed_func
            cls.action_performed_param = action_performed_param

        @classmethod
        def is_performed(cls, data):
            try:
                return cls.is_performed_func.call(data, *cls.is_performed_param)
            except Exception as e:
                ex = ScriptError()
                ex.add_message("Exception Message", str(e))
                ex.add_message("Exception Type", type(e).__name__)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                for trace in traceback.extract_tb(exc_traceback)[1:]:
                    code = ['', '"""python']
                    filename = trace[0]
                    line_no = trace[1]
                    method = trace[2]
                    try:
                        # Donne un aperçu du fichier à la ligne donnée
                        with open(filename, 'r') as file_handler :
                            lines = file_handler.readlines()[line_no-5:line_no+4]
                            it = line_no - 4
                            for line in lines:
                                line = line.rstrip()
                                delimiter = "!!!" if it == line_no else ">>>"
                                code.append("{:3} {} {} ".format(it, delimiter, line))
                                it += 1
                        ex.add_message("Code", '\n'.join(code) + '\n"""')
                    except Exception:
                        pass
                    ex.add_message("Line", line_no)
                    ex.add_message("Method", method)
                    ex.add_message("File", filename)
                    ex.add_message('', '')
                raise ex


        @classmethod
        def action_performed(cls, data):
            try:
                return cls.action_performed_func.call(data, *cls.action_performed_param)
            except Exception as e:
                ex = ScriptError()
                ex.add_message("Exception Message", str(e))
                ex.add_message("Exception Type", type(e).__name__)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                for trace in traceback.extract_tb(exc_traceback)[1:]:
                    filename = trace[0]
                    line_no = trace[1]
                    method = trace[2]
                    code = ['', '"""python {} {}#{}'.format(filename, method, line_no)]

                    try:
                        # Donne un aperçu du fichier à la ligne donnée
                        with open(filename, 'r') as file_handler :
                            lines = file_handler.readlines()[line_no-5:line_no+4]
                            it = line_no - 4
                            for line in lines:
                                line = line.rstrip()
                                delimiter = "!!!" if it == line_no else ">>>"
                                code.append("{:3} {} {} ".format(it, delimiter, line))
                                it += 1
                        ex.add_message("Code", '\n'.join(code) + '\n"""')
                    except Exception:
                        pass

                    ex.add_message("Line", line_no)
                    ex.add_message("Method", method)
                    ex.add_message("File", filename)
                    ex.add_message('', '')
                raise ex

    # Création d'un nom suffisament joli pour le debug
    AnonymousTrigger.__name__ = "_Trigger_{}".format(action_name)
    # Définition statique de la classe nouvellement crée.
    AnonymousTrigger._define_functions(is_performed_func,\
        is_performed_param,\
        action_performed_func,\
        action_performed_param)
    return AnonymousTrigger
