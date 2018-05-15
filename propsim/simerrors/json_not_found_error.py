#!/usr/bin/env python
# -*-coding:utf-8-*-
from json_error import JSONError

class JSONNotFoundError(JSONError):
    """ Script introuvable"""
    def __init__(self):
        super(JSONNotFoundError, self).__init__()
