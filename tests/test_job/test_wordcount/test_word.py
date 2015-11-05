# -*- coding: utf-8 -*-
from nose.tools import assert_equals
from collections import Counter
from job.wordcount.word import Word


class test_Word:

    def test__init__(self):
        args = {'surface': 'test', 'count': 1, 'distribution': Counter({'test': 1}),
                'distance': None, 'time': 0, 'x': 0, 'y': 0}
        self.wc = Word(**args)
        for (idx, val) in args.items():
            assert getattr(self.wc, idx) == val