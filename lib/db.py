# -*- coding: utf-8 -*-
import shelve
import os
from . import path


def Shelve():
    shelve_file = os.path.join(path.datadir(), 'atango.shelve')
    flag = 'w' if os.path.exists(shelve_file) else 'c'
    return shelve.open(shelve_file, flag=flag)
