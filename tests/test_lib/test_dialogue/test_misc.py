# -*- coding: utf-8 -*-
from nose.tools import assert_true
from lib.dialogue import misc


def test_random_choice():
    actual = misc._random_choice()
    assert_true(actual)
    assert_true(isinstance(actual, str))
