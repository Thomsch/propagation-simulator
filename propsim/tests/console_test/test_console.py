#!/usr/bin/env python
# -*-coding:utf-8-*-


import os
from nose.tools import *
from console.console import *
from PySide.QtGui import QApplication

class TestBuilder(object):
    
    def __init__(self, *args, **kwargs):
        object.__init__(self, *args, **kwargs)
        self.app = QApplication
        self.console = Console
    
    def test_init_console(self):
        ### TODO
        pass
        
    def text_push_text(self):
        ### TODO
        pass
        