# -*- coding: utf-8 -*-
from nose.tools import assert_equals
from common import normalize


def test_shorten_repeat():
    got = normalize.shorten_repeat('kieeee', 2)
    assert_equals(got, 'kiee')
    got = normalize.shorten_repeat(u'無駄無駄無駄', 1)
    assert_equals(got, u'無駄')


def test_remove_useless_symbol():
    text = normalize.USELESS_SYMBOL_CHARS
    got = normalize.remove_useless_symbol(text)
    assert_equals(got, '')


def test_normalize():
    got = normalize.normalize(u'あいぼんのおまんこを指で開いてｸﾁｭｸﾁｭしたいよおおーう')
    assert_equals(got, u'あいぼんのおまんこを指で開いてクチュクチュしたいよーう')


def test_normalize_word():
    got = normalize.normalize_word(u'おマンコ')
    assert_equals(got, u'おまんこ')


def test_htmlentity2unicode():
    got = normalize.htmlentity2unicode('&nbsp;')
    assert_equals(got, u'\xa0')
    got = normalize.htmlentity2unicode('&hearts;')
    assert_equals(got, u'♥')


def test_remove_emoticon():
    emoticons = (u'(;´Д`)', u'ヽ(´ー｀)ノ', u'v(*ﾟД､`)v', u'(;´Д`)人(;´Д`)')
    for emoticon in emoticons:
        got = normalize.remove_emoticon(emoticon)
        assert_equals(got, '')


class test_SynonymUnification(object):

    def __init__(self):
        self.su = normalize.SynonymUnification()

    def test_unify(self):
        text = 'ぱつぱつぱんつ'
        assert_equals(self.su.unify(text), 'ぴっちりパンツ')
