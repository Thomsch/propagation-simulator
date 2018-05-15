#!/usr/bin/env python
# -*-coding:utf-8-*-
from script_error import ScriptError

class TerrainNotFound(ScriptError):
    """ Le terrain désigné n'existe pas """
    def __init__(self):
        super(TerrainNotFound, self).__init__()
