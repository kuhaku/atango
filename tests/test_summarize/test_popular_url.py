# -*- coding: utf-8 -*-
from nose.tools import assert_equals, assert_true
from summarize import popular_url


TITLES = (("Twitter / atango", "atango"), ("ぁ単語さんはTwitterを使っています", "ぁ単語"), 
          ("おっぱいブログ Powered by アメブロ", "おっぱいブログ"))

class test_PopularUrl(object):

    def __init__(self):
        self.purl = popular_url.PopularUrl()

    def test__count_url(self):
        for (title, desired) in TITLES:
            actual = self.purl._shorten_title(title)
            assert_equals(actual, desired)
        assert_equals(self.purl._shorten_title('雫...'), '雫…')
        title = '女性声優画像bot on Twitter: "内田真礼 http://t.co/s0WPLYOyYV"'
        desired = '女性声優画像bot:"内田真礼"'
        assert_equals(self.purl._shorten_title(title), desired)

    def test__shorten_title(self):
        pass

    def test__get_title(self):
        pass

    def test_run(self):
        pass
