# -*- coding: utf-8 -*-
from lib.dialogue import misc


def test_random_choice():
    actual = misc._random_choice()
    assert next(actual)
    assert isinstance(next(actual), str) is True


def test_respond_by_rule(*arg):
    actual = misc.respond_by_rule('プレゼント')
    assert next(actual)['text'].startswith('%nameに') is True


def test_give_present():
    actual = misc.give_present('プレゼント')
    assert actual['text'].startswith('%nameに') is True
