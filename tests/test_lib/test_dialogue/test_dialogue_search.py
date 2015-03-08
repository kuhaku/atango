# -*- coding: utf-8 -*-
from nose.tools import assert_true, assert_false, assert_equals
from lib.dialogue import dialogue_search as dial_search


def test__validate_query():
    query = ['私', '殺す', '思い出', '']
    actual = dial_search._validate_query(query)
    desired = set(['私', '殺す', '思い出'])
    assert_equals(set(actual), desired)


def test__validate_post():
    assert_true(dial_search._validate_post({'q1': 'おっぱい', 'text': 'マミさん'}))
    assert_false(dial_search._validate_post({'author': 'マミ', 'text': 'マミさん'}))
    assert_false(dial_search._validate_post({'text': 'はい'}))
    assert_false(dial_search._validate_post({'text': 'きええええ'*200}))
    assert_equals(dial_search._validate_post({'q1': '', 'text': '<A href=\"url\">url</A>'}), '')


def test__extract_response_by_search():
    actual = dial_search._extract_response_by_search(['マミさん', 'おっぱい'], False)
    assert_true(list(actual))


def test_respond():
    actual = dial_search.respond('マミさんのおっぱい')
    assert_true(list(actual))
    actual = dial_search.respond('我爱你')
    assert_false(list(actual))
