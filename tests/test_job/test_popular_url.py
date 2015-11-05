# -*- coding: utf-8 -*-
from nose.tools import assert_equals, nottest
from job import popular_url


TITLES = (("Twitter / atango", "atango"), ("ぁ単語さんはTwitterを使っています", "ぁ単語"), 
          ("おっぱいブログ Powered by アメブロ", "おっぱいブログ"))


class test_PopularUrl(object):

    def __init__(self):
        self.purl = popular_url.PopularUrl()

    def test__count_url(self):
        for (title, desired) in TITLES:
            actual = self.purl._shorten_title(title)
            assert actual == desired
        assert self.purl._shorten_title('雫...') == '雫…'
        title = '女性声優画像bot on Twitter: "内田真礼 http://t.co/s0WPLYOyYV"'
        desired = '女性声優画像bot"内田真礼"'
        assert self.purl._shorten_title(title) == desired

    @nottest
    def test__shorten_title(self):
        pass

    @nottest
    def test__get_title(self):
        pass

    def test_extract_tweet_id(self):
        url = 'https://twitter.com/sw_words/status/346716382630645760'
        assert self.purl.extract_tweet_id(url) == '346716382630645760'
        url = 'https://twitter.com/sw_words/status/346716382630645760/photo/1'
        assert self.purl.extract_tweet_id(url) == '346716382630645760'

    @nottest
    def test_calc_tweet_length(self):
        pass

    @nottest
    def test_run(self):
        pass