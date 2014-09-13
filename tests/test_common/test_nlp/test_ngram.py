# -*- coding: utf-8 -*-
from nose.tools import assert_equals
from common.nlp import ngram


def test_to_ngrams():
    got = ngram.to_ngrams(u'おまんこ', 4)
    assert_equals(got, [[u'おま', u'まん', u'んこ'], [u'おまん', u'まんこ'], [u'おまんこ']])


def test_to_ngram():
    got = ngram.to_ngram(u'おまんこ', 2)
    assert_equals(got, [u'おま', u'まん', u'んこ'])
