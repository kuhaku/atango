# -*- coding: utf-8 -*-
from nose.tools import assert_true, assert_equals
from lib.dialogue import qa


def test__extract_oshiete_answer():
    posts = [{'text': 'マミは'},
             {'text': 'マミさんはいるかなぁ？'},
             {'text': 'マミさんはかわいい'}]
    actual = qa._extract_oshiete_answer('マミ', posts)
    assert_equals(actual, 'マミさんはかわいい')


def test_respond_oshiete():
    text = 'マミさんって何'
    actual = qa.respond_oshiete(text)
    assert_true(actual.startswith('マミさん'))


def test__build_what_who_query():
    actual = qa._build_what_who_query('誰がかわいい？')
    assert_equals(actual, 'かわいい')

    actual = qa._build_what_who_query('何がおかしい')
    assert_equals(actual, 'おかしい')


def test_respond_what_who():
    actual = qa.respond_what_who('誰がかわいい')
    assert_true('がかわいい' in actual or 'はかわいい' in actual)
