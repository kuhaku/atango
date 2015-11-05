# -*- coding: utf-8 -*-
from nose.tools import assert_equals
from lib import mycodecs


def test_normalize_encoding():
    actual = mycodecs.normalize_encoding('SHIFT_JIS')
    assert actual == 'cp932'

    actual = mycodecs.normalize_encoding('windows-31j')
    assert actual == 'cp932'


def test_decode():
    actual = mycodecs.decode('おまんこ'.encode('cp932'), 'SHIFT_JIS')
    assert actual == 'おまんこ'

    actual = mycodecs.decode('おまんこ'.encode('utf8'), 'iso-8859-1')
    assert actual == 'おまんこ'

    cp50220 = b'\x1b$B|q|r|s|t|u|v|w|x|y|z|||}|~\x1b(B'
    actual = mycodecs.decode(cp50220)
    assert actual == 'ⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹ¦＇＂'