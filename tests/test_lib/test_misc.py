# -*- coding: utf-8 -*-
from nose.tools import assert_equals, assert_raises
from lib import misc


def test_choice():
    got = misc.choice('aaaa')
    assert_equals(got, 'a')


def test_nones():
    got = misc.nones(2)
    assert_equals(got, [None, None])
    got = misc.nones(2, 2)
    assert_equals(got, [[None, None], [None, None]])
    assert_raises(ValueError, misc.nones, 1, 0.5)
    assert_raises(ValueError, misc.nones, 0.5, 1)
    assert_raises(ValueError, misc.nones, 0, 1)
    assert_raises(ValueError, misc.nones, 1, 0)


def test_map_dict():
    got = misc.map_dict(int, {1: '1', 2: '2'})
    assert_equals(got, {1: 1, 2: 2})
