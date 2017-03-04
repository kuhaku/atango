# -*- coding: utf-8 -*-
import bz2
import os
import json
from configparser import SafeConfigParser
from . import pathutil, mycodecs


def read_text_file(filename, encoding=''):
    """
    Read text file with decoding to unicode
    Params:
        <str> filename
        <str> encoding
    Return:
        <str> text
    """
    opener = bz2.BZ2File if filename.endswith('.bz2') else open
    with opener(filename, 'rb') as fd:
        text = fd.read()
    if encoding:
        return text.decode(encoding, 'replace')
    return mycodecs.decode(text, encoding, 'replace')


def read(filename, data=False, encoding=''):
    _dir = pathutil.datadir() if data else pathutil.cfgdir()
    if filename.endswith('.cfg'):
        cfg = os.path.join(_dir, filename)
        config_parser = SafeConfigParser()
        config_parser.read(cfg)
        return dict(config_parser)
    elif filename.endswith('.json'):
        return json.load(open(os.path.join(_dir, filename), 'r', encoding='utf-8'))
    elif filename.endswith('.txt'):
        filename = os.path.join(_dir, filename)
        text = read_text_file(filename, encoding)
        return text.splitlines()
