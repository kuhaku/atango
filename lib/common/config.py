# -*- coding: utf-8 -*-
import os
import json
from configparser import ConfigParser, SafeConfigParser
from . import file_io


def __basedir():
    wdir = os.path.abspath(os.path.dirname(__file__))
    return os.path.normpath(os.path.join(wdir, '../../'))


def __get_path(dirname):
    return os.path.normpath(os.path.join(__basedir(), dirname))


def datadir():
    return __get_path('data')


def cfgdir():
    return __get_path('cfg')


def logdir():
    return __get_path('logdir')


def read(filename, encoding=''):
    if filename.endswith('.cfg'):
        cfg = os.path.join(cfgdir(), filename)
        config_parser = SafeConfigParser()
        config_parser.read(cfg)
        return config_parser
    elif filename.endswith('.json'):
        return json.load(open(os.path.join(cfgdir(), filename), 'r', encoding='utf-8'))
    elif filename.endswith('.txt'):
        path = os.path.join(cfgdir(), filename)
        text = file_io.read_text_file(path, encoding)
        return text.splitlines()
