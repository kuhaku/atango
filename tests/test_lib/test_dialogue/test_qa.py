# -*- coding: utf-8 -*-
from lib.dialogue import qa
import pytest

def test__extract_oshiete_answer():
    posts = [{'text': 'マミは'},
             {'text': 'マミさんはいるかなぁ？'},
             {'text': 'マミさんはかわいい'}]
    actual = next(qa._extract_oshiete_answer('マミ', posts))
    assert actual == 'マミさんはかわいい'


@pytest.fixture(scope="module")
def test_respond_oshiete():
    text = 'マミさんって何'
    actual = next(qa.respond_oshiete(text))
    assert actual.startswith('マミさん') is True

def test__build_what_who_query():
    actual = qa._build_what_who_query('誰がかわいい？')
    assert actual == 'かわいい'

    actual = qa._build_what_who_query('何がおかしい')
    assert actual == 'おかしい'

@pytest.fixture(scope="module")
def test_respond_what_who():
    actual = next(qa.respond_what_who('誰がかわいい'))
    assert ('がかわいい' in actual or 'はかわいい' in actual) is True
