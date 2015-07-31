# -*- coding: utf-8 -*-
import random
from nose.tools import assert_equals, assert_true, assert_false, assert_raises
from lib import misc


def test_command():
    assert_true(misc.command('date')[0])


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


def test_has_substr():
    iterable = ('マミさん', 'チーズケーキ')
    assert_true(misc.has_substr(iterable, 'マミ'))
    assert_false(misc.has_substr(iterable, 'ほむ'))


def test_retry():
    @misc.retry(1000, interval=0.001)
    def testfunc():
        if random.randint(0, 1):
            raise Exception
        return True

    assert_true(testfunc())
