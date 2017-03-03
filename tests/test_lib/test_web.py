# -*- coding: utf-8 -*-
from lib import web


def test_open_url():
    url = 'http://misao.on.arena.ne.jp/cgi-bin/bbs.cgi'
    got = web.open_url(url)
    assert 'あやしいわーるど' in got
