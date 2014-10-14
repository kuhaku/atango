# -*- coding: utf-8 -*-
from nose.tools import assert_equals, assert_true
from collections import defaultdict
from summarize.ome import Ome


class test_Ome(object):

    def __init__(self):
        self.ome = Ome()

    def test_get_post_res_pairs(self):
        posts = {'1': {'q1': '浜松って何があんの？(;´Д`)', 'text': 'うなぎ'},
                 '2': {'q1': '浜松って何があんの？(;´Д`)', 'text': 'うなぎ(;´Д`)'}
                }
        actual = self.ome.get_post_res_pairs(posts)
        desired = defaultdict(list)
        desired['浜松って何があんの？(;´Д`)'] = ['うなぎ', 'うなぎ(;´Д`)']
        actual = {k: set(v) for (k, v) in actual.items()}
        desired = {k: set(v) for (k, v) in desired.items()}
        assert_equals(actual, desired)

    def test_simplify(self):
        assert_equals(self.ome.simplify('パンシ！？(ﾟДﾟ)'), 'パンシ')

    def test_levenshtein_per_char(self):
        pair = ['ぱんし', 'ぱんつ']
        actual = self.ome.levenshtein_per_char(pair)
        assert_equals(actual, 1 - 1/6)
        pair = ['ぱんし', 'ぱんし']
        actual = self.ome.levenshtein_per_char(pair)
        assert_equals(actual, 1)

    def test_levenshtein_per_word(self):
        pair = ['牛乳だ', '牛乳です']
        actual = self.ome.levenshtein_per_word(pair)
        assert_equals(actual, 1)

    def test_levenshtein_per_char_yomi(self):
        pair = ['まみ', 'マミ']
        actual = self.ome.levenshtein_per_char_yomi(pair)
        assert_equals(actual, 1)

    def test_lcs(self):
        pair = ['巴マミ', 'マミ']
        actual = self.ome.lcs(pair)
        assert_equals(actual, 2 / 2.5)

    def test_is_ome(self):
        pairs = (
            ('ぱんし', 'ぱんし'), ('牛乳だ', '牛乳です'),
            ('まみ', 'マミ'), ('巴マミ', 'マミ')
        )
        for pair in pairs:
            actual = self.ome.is_ome(*pair)
            print(pair)
            assert_true(actual)


    def test_run(self):
        pass
