# -*- coding: utf-8 -*-
import bz2
import nkf


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


def read_text_file(path, encoding=''):
    """
    Read text file with decoding to unicode
    Params:
        <str> path
        <str> encoding
    Return:
        <str> text
    """
    opener = bz2.BZ2File if path.endswith('.bz2') else open
    with opener(path, 'rb') as fd:
        text = fd.read()
    if encoding:
        return text.decode(encoding, 'replace')
    return decode_by_guessing(text)
