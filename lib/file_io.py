# -*- coding: utf-8 -*-
import bz2
import nkf
import os
import json
from configparser import SafeConfigParser
from . import path


def decode_by_guessing(text):
    """
    decode unicode string by guessing character encoding
    Param:
        <str> text
    Return:
        <str> text
    """
    encoding = nkf.guess(text)
    if encoding in ('BINARY', 'ISO-8859-1'):
        encoding = 'utf8'
    return text.decode(encoding, 'replace')


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
    return decode_by_guessing(text)


def read(filename, encoding=''):
    if filename.endswith('.cfg'):
        cfg = os.path.join(path.cfgdir(), filename)
        config_parser = SafeConfigParser()
        config_parser.read(cfg)
        return dict(config_parser)
    elif filename.endswith('.json'):
        return json.load(open(os.path.join(path.cfgdir(), filename), 'r', encoding='utf-8'))
    elif filename.endswith('.txt'):
        filename = os.path.join(path.cfgdir(), filename)
        text = read_text_file(filename, encoding)
        return text.splitlines()
