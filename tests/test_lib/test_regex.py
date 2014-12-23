# -*- coding: utf-8 -*-
from nose.tools import assert_true, assert_equals
from lib import regex


def test_re_url():
    urls = ('http://qwerty.on.arena.ne.jp/cgi-bin/bbs.cgi', 'https://https.test',
            'http://port.test:8080', 'http://ja.wikipedia.org/wiki/%E3%81%86%E3%81%A4')
    for url in urls:
        actual = regex.re_url.search(url)
        assert_true(actual)
        assert_equals(actual.group(0), url)


def test_re_html_tag():
    assert_equals(regex.re_html_tag.sub('', '<ENEMA>神岸あかり</ENEMA>'), '神岸あかり')
    assert_equals(regex.re_html_tag.sub('', '<a id="1">1</a>'), '1')


def test_re_a_tag():
    assert_equals(regex.re_a_tag.sub('', '<a href="#1">1</a>'), '')
    assert_equals(regex.re_a_tag.sub('', '<A id="1">1</A>'), '')
