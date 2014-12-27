# -*- coding: utf-8 -*-
from nose.tools import assert_equals
from lib import multiprocess


class test_Pool(object):

    def __init__(self):
        self.pool = multiprocess.Pool()

    def test_apply(self):
        actual = self.pool.apply(str, [1,])
        assert_equals(actual, '1')

    def test_apply_async(self):
        actual = self.pool.apply_async(str, [1,])
        assert_equals(actual.get(), '1')

    def test_map(self):
        actual = self.pool.map(int, range(10))
        assert_equals(actual, list(range(10)))

    def test_map_async(self):
        actual = self.pool.map_async(int, range(10))
        assert_equals(list(actual.get(timeout=5)), list(range(10)))

    def test_imap(self):
        actual = self.pool.imap(int, range(10))
        assert_equals(list(actual), list(range(10)))

    def test_imap_unordered(self):
        actual = self.pool.imap(int, range(10))
        assert_equals(set(actual), set(range(10)))
