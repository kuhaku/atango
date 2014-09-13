# -*- coding: utf-8 -*-
from nose.tools import assert_true
from common import web


def test_open_url():
    url = 'http://qwerty.on.arena.ne.jp/'
    got = web.open_url(url)
    assert_true(u'あやしいわーるど' in got)
