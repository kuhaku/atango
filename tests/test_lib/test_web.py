# -*- coding: utf-8 -*-
from lib import web


def test_open_url():
    url = 'http://qwerty.on.arena.ne.jp/'
    got = web.open_url(url)
    assert 'あやしいわーるど' in got
