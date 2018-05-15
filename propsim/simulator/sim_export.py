#!/usr/bin/env python
# -*-coding:utf-8-*-
import time, datetime
from simerrors import *
from config import *
import os
from simutils import *
from builder import *

class SimExport(object):
    """Classe à utiliser pour l'export des données dans des fichiers de log."""

    get_iteration_func = None
    simulation_id = datetime.datetime.\
        fromtimestamp(time.time()).strftime('%Y%m%d %H-%M-%S')

    filenames = dict()

    export_enabled = False
    export_param = None

    @classmethod
    def _register_get_iteration(cls, get_iteration_func):
        cls.get_iteration_func = get_iteration_func
            # Crée la structure de dossier pour les logs.
        if cls.export_enabled :
            try:
                os.makedirs(Globals._user_log_dir(cls.simulation_id))
            except Exception as e :
                pass

    @classmethod
    def write_file(cls, file_name, object_dict):
        if not cls.export_enabled:
            return

        sep = cls.export_param['separator']
        new_line = cls.export_param['new_line']
        ext = cls.export_param['extension']
        object_dict["__iteration"] = str(cls.get_iteration_func())

        file_name = file_name + '.' + ext
        keys = None
        given_keys = sorted(object_dict.keys())

        if file_name not in cls.filenames:
            keys = given_keys
            abs_filename = Globals._user_log_path(cls.simulation_id, file_name)
            cls.__init_file(abs_filename, keys, sep, new_line)
            cls.filenames[file_name] = (abs_filename, keys)
        else:
            # Vérification que toutes les clés du fichiers sont données
            # Evite les fichiers de logs incohérents.
            (abs_filename, keys) = cls.filenames[file_name]
            if len(keys) > len(given_keys):
                e = PropsimError()
                e.add_message("Exception Message", "Too much keys given for export")
                e.add_message("Key length", len(given_keys))
                e.add_message("Export filename", file_name)

            for key in given_keys :
                if key not in keys:
                    # Pas de valeur apparente pour l'attribut
                    e = PropsimError()
                    e.add_message("Exception Message", "Key missing during export")
                    e.add_message("Key name", key)
                    e.add_message("Export file", file_name)
                    raise e


        values = [object_dict[key] for key in keys]
        with open(abs_filename, "a") as output_file:
            output_file.write(sep.join([str(v) for v in values]) + new_line)


    @classmethod
    def __init_file(cls, abs_filename, keys, sep, new_line):
        """ Ecrit le fichier de logs pour la première fois. """
        with open(abs_filename, "w") as output_file:
            output_file.write(sep.join(keys) + new_line)

