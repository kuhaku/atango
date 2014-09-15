# -*- coding: utf-8 -*-
from nose.tools import assert_equals, assert_true
from common.nlp import mecab


def test_is_target_pos():
    feature = '名詞,サ変接続,*,*,*,*,テスト,テスト,テスト,,'
    pos = '名詞,サ変接続'
    assert_true(mecab._is_target_pos(feature, pos))


def test_extract_rootform():
    feature = '動詞,自立,*,*,一段,命令ro,寝る,ネロ,ネロ'
    assert_equals(mecab._extract_rootform(feature, dic='IPA'), u'寝る')


def test_extract_surface():
    m = mecab.MeCabWrapper()
    nodes = [n for n in m.parse_to_node('寝ろ')]
    assert_equals(mecab._extract_surface(nodes[0]), u'寝ろ')
    assert_equals(mecab._extract_surface(nodes[0], True), u'寝る')


def test_extract_phrase():
    m = mecab.MeCabWrapper()
    nodes = [n for n in m.parse_to_node('環境音楽だ')]
    assert_equals(mecab._extract_phrase(nodes, '名詞'), [u'環境音楽'])


def test_extract_word():
    got = mecab.extract_word('環境音楽だ', '名詞')
    assert_equals(got, [u'環境', u'音楽'])
    got = mecab.extract_word('環境音楽だ', '名詞', phrase=True)
    assert_equals(got, [u'環境', u'音楽', u'環境音楽'])
    got = mecab.extract_word('寝ろ', '動詞', rootform=True)
    assert_equals(got, [u'寝る'])


def test_count_word():
    got = mecab.count_word('環境音楽だ', 'noun', phrase=False)
    assert_equals(got, {u'環境': 1, u'音楽': 1})


def test_count_doc():
    got = mecab.count_doc('環境\n音楽'.splitlines())
    assert_equals(got, {u'環境': 1, u'音楽': 1})
