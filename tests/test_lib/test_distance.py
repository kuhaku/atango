# -*- coding: utf-8 -*-
from lib import distance


def test_levenshtein():
    got = distance.levenshtein('mami', 'pami', 1, 1, 1)
    assert got == 1
    got = distance.levenshtein('mami', 'pami', 1, 1, 0)
    assert got == 0
    got = distance.levenshtein('unko', 'unk', 1, 3, 1)
    assert got == 3
    got = distance.levenshtein('chiko', 'chinko', 3, 1, 1)
    assert got == 3


def test_LCCS():
    assert len(distance.LCCS('mamipai', 'tomoemami', 4)) == 4
