# -*- coding: utf-8 -*-
from nose.tools import assert_true
from lib.dialogue import misc


def test_random_choice():
    actual = misc._random_choice()
    assert_true(next(actual))
    assert_true(isinstance(next(actual), str))


def test_respond_by_rule(*arg):
    actual = misc.respond_by_rule('プレゼント')
    assert_true(next(actual)['text'].startswith('%nameに'))


def test_give_present():
    actual = misc.give_present('プレゼント')
    assert_true(actual['text'].startswith('%nameに'))
