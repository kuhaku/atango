# -*- coding: utf-8 -*-
from nose.tools import assert_equals
from common import distance


def test_levenshtein():
    got = distance.levenshtein('mami', 'pami', 1, 1, 1)
    assert_equals(got, 1)
    got = distance.levenshtein('mami', 'pami', 1, 1, 0)
    assert_equals(got, 0)
    got = distance.levenshtein('unko', 'unk', 1, 3, 1)
    assert_equals(got, 3)
    got = distance.levenshtein('chiko', 'chinko', 3, 1, 1)
    assert_equals(got, 3)


def test_LCCS():
    assert_equals(len(distance.LCCS('mamipai', 'tomoemami', 6)), 4)
