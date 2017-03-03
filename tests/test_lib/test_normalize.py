# -*- coding: utf-8 -*-
from nose.tools import assert_equals
from lib import normalize


def test_shorten_repeat():
    got = normalize.shorten_repeat('kieeee', 2)
    assert got == 'kiee'
    got = normalize.shorten_repeat(u'無駄無駄無駄', 1)
    assert got == u'無駄'


def test_remove_useless_symbol():
    text = normalize.USELESS_SYMBOL_CHARS
    got = normalize.remove_useless_symbol(text)
    assert got == ''


def test_normalize():
    got = normalize.normalize(u'あいぼんのおまんこを指で開いてｸﾁｭｸﾁｭしたいよおおーう')
    assert got == u'あいぼんのおまんこを指で開いてクチュクチュしたいよーう'


def test_normalize_word():
    got = normalize.normalize_word(u'おマンコ')
    assert got == u'おまんこ'


def test_remove_emoticon():
    emoticons = (u'(;´Д`)', u'ヽ(´ー｀)ノ', u'v(*ﾟД､`)v', u'(;´Д`)人(;´Д`)')
    for emoticon in emoticons:
        got = normalize.remove_emoticon(emoticon)
        assert got == ''


class test_SynonymUnification(object):

    def __init__(self):
        self.su = normalize.SynonymUnification()

    def test_unify(self):
        text = 'ぱつぱつぱんつ'
        assert self.su.unify(text) == 'ぴっちりパンツ'
