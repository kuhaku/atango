# -*- coding: utf-8 -*-
from lib.dialogue import dialogue_search as dial_search


def test__validate_query():
    query = ['私', '殺す', '思い出', '']
    actual = dial_search._validate_query(query)
    desired = set(['私', '殺す', '思い出'])
    assert set(actual) == desired


def test__validate_post():
    assert dial_search._validate_post({'q1': 'おっぱい', 'text': 'マミさん'})
    assert dial_search._validate_post({'author': 'マミ', 'text': 'マミさん'}) is False
    assert dial_search._validate_post({'text': 'はい'}) is False
    assert dial_search._validate_post({'text': 'きええええ'*200}) is False
    assert dial_search._validate_post({'q1': '', 'text': '<A href=\"url\">url</A>'}) == ''


def test__extract_response_by_search():
    actual = dial_search._extract_response_by_search(['マミさん', 'おっぱい'], False)
    assert list(actual)


def test_respond():
    actual = dial_search.respond('マミさんのおっぱい')
    assert list(actual)
    actual = dial_search.respond('我爱你')
    assert list(actual) == []
