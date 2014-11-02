# -*- coding: utf-8 -*-
from nose.tools import nottest, assert_true, assert_false, assert_equals
from lib.dialogue import dialogue_search as dial_search
from lib import web


def test__validate_query():
    query = ['私', '殺す', '思い出', '']
    actual = dial_search._validate_query(query)
    desired = set(['私*', '殺す', '思い出'])
    assert_equals(set(actual), desired)


def test__is_valid_post():
    assert_true(dial_search._is_valid_post('マミさん'))
    assert_false(dial_search._is_valid_post('はい'))
    assert_false(dial_search._is_valid_post('きええええ'*200))


@nottest
def test__choice_res():
    html = web.open_url('http://usamin.mine.nu/cgi/swlog?b=qwerty&s=18146945')
    actual = dial_search._choice_res(html, 'マミさん', False)
    desired = 'でもあの人悪党なんだろうなぁと思うとなんか(;´Д`)'
    assert_equals(actual, desired)


@nottest
def test__extract_response_by_search():
    actual = dial_search._extract_response_by_search(['マミさん', 'おっぱい'], False)
    desired = 'ソウルジェムプリンがいいな(;´Д`)カラメルソースかき混ぜて濁らせるの'
    assert_equals(actual, desired)


@nottest
def test__extract_response_from_log():
    pass


@nottest
def test_respond():
    """
    actual = resgen.respond('マミさんって何？')
    print(actual)
    assert_true(actual.startswith('マミさん'))
    time.sleep(0.5)
    actual = resgen.respond('誰がかわいい？')
    print(actual)
    assert_true('かわいい' in actual)
    """
