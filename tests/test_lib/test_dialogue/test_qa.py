# -*- coding: utf-8 -*-
from nose.tools import nottest, assert_true
from lib.dialogue import qa


@nottest
def test__extract_oshiete_answer():
    pass

@nottest
def test_respond_oshiete():
    text = 'マミさんって何'
    actual = qa.respond_oshiete(text)
    print(actual)
    assert_true(actual.startswith('マミさん'))

@nottest
def test__build_what_who_query():
    pass

@nottest
def test__extract_what_answer():
    pass

def test_respond_what_who():
    actual = qa.respond_what_who('誰がかわいい')
    print(actual)
    assert_true('かわいい' in actual)
