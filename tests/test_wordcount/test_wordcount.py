# -*- coding: utf-8 -*-
from nose.tools import assert_equals, assert_true
from datetime import datetime
from collections import Counter
from wordcount import wordcount
from wordcount.word import Word


class test_WordCount:

    def __init__(self):
        self.wc = wordcount.WordCount()

    def test_get_log(self):
        self.wc._get_log('', {'hour': 1})
        now = datetime.now()
        if now.hour == 0:
            expect_start_hour = 23
            expect_end_hour = 24
        else:
            expect_start_hour = now.hour - 1
            expect_end_hour = now.hour
        assert_equals(self.wc.start_hour, str(expect_start_hour))
        assert_equals(self.wc.end_hour, str(expect_end_hour))

    def test_sort_by_time(self):
        posts = [{'time': 1}, {'time': 2}]
        got = self.wc._sort_by_time(posts)
        assert_equals(got, [{'time': 1}, {'time': 2}])

    def test_is_valid_post(self):
        log = {'text': 'x'}
        assert_true(self.wc.is_valid_post(log))
        assert_true(not self.wc.is_valid_post({}))
        log = {'text': 'x', 'author': u'アニメ時報'}
        assert_true(not self.wc.is_valid_post(log))

    def test_calc_avg_time(self):
        word = Word(count=2, time=3)
        self.wc.start_time = 0
        assert_equals(self.wc.calc_avg_time(word, 7), 5)

    def test_merge_counter(self):
        self.wc.plot_wordmap = False
        counter = Counter({'x': 1})
        word = Word(count=1, distribution=Counter({'x': 1, 'y': 1}))
        total_words = {'x': word}
        got = self.wc.merge_counter(counter, total_words)
        assert_equals(got['x'].count, 2)
        assert_equals(got['x'].distribution, Counter({'x': 2, 'y': 1}))

    def test_sort_by_keys_length(self):
        vals = [Word(surface='xx', count=2),
                Word(surface='x', count=0)]
        mapping = dict(zip(('xx', 'x'), vals))
        gots = self.wc.sort_by_keys_length(mapping)
        for got, expect in zip(gots, vals):
            assert_equals(got[1].surface, expect.surface)
            assert_equals(got[1].count, expect.count)

    def test_gen_report(self):
        word_x = Word(surface='word_x', count=2)
        word_y = Word(surface='word_y', count=1)
        self.wc.start_hour = 0
        self.wc.end_hour = 1
        got = self.wc.gen_report({'word_x': word_x, 'word_y': word_y})
        expect = u'0~1時の＠上海:\n word_x：2, word_y：1'
        assert_equals(got, expect)
