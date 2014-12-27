# -*- coding: utf-8 -*-
import os


def _basedir():
    wdir = os.path.abspath(os.path.dirname(__file__))
    return os.path.normpath(os.path.join(wdir, '../'))


def _get_path(dirname):
    return os.path.normpath(os.path.join(_basedir(), dirname))


def datadir():
    return _get_path('data')


def cfgdir():
    return _get_path('cfg')


def logdir():
    return _get_path('logs')


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return True
