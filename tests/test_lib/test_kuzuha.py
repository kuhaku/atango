# -*- coding: utf-8 -*-
import datetime
from unittest.mock import patch
from nose.tools import assert_equals, nottest
from lib import kuzuha


DEFAULT_PARAMS = {
    's1': '0',
    'e1': '0',
    's2': '24',
    'e2': '0',
}
DEFAULT_PARAMS_DETAIL = {
    's1': '0',
    'e1': '0',
    's2': '24',
    'e2': '0',
    'kwd': '',
    'ao': 'o',
    'j': 'checked',
    'c': 100,
    'btn': 'checked',
    'tt': 'a',
    'alp': 'checked',
    'g': 'checked',
    'm': 'g',
    'k': '%82%A0',
    'sv': 'on'
}

def test_gen_params_by_day():
    date_range = {'day': 3}
    now = datetime.datetime(2011, 2, 14)
    params = DEFAULT_PARAMS.copy()
    got_params = kuzuha._gen_params_by_day(date_range, now, params)

    expect = {
        'chk20110211.dat': 'checked',
        'chk20110211.dat': 'checked',
        'chk20110212.dat': 'checked',
        'chk20110213.dat': 'checked',
        'chk20110214.dat': 'checked',
        's1': '0',
        'e1': '0',
        's2': '24',
        'e2': '0'
    }
    assert got_params == expect


def test_gen_params_by_hour():
    date_range = {'hour': 1}
    now = datetime.datetime(2011, 2, 14, 1, 55)
    params = DEFAULT_PARAMS.copy()
    got_params = kuzuha._gen_params_by_hour(date_range, now, params)
    expect = {
        'chk20110214.dat': 'checked',
        's1': '0',
        'e1': '0',
        's2': '1',
        'e2': '0'
    }
    assert got_params == expect

    # when crossing days
    date_range = {'hour': 1}
    now = datetime.datetime(2011, 2, 14, 0, 0)
    params = DEFAULT_PARAMS.copy()
    got_params = kuzuha._gen_params_by_hour(date_range, now, params)
    expect = {
        'chk20110213.dat': 'checked',
        's1': '23',
        'e1': '0',
        's2': '24',
        'e2': '0'
    }
    assert got_params == expect


def test_gen_params_by_minute():
    date_range = {'minute': 10}
    now = datetime.datetime(2011, 2, 14, 1, 55)
    params = DEFAULT_PARAMS.copy()
    got_params = kuzuha._gen_params_by_minute(date_range, now, params)
    expect = {
        'chk20110214.dat': 'checked',
        's1': '1',
        'e1': '45',
        's2': '1',
        'e2': '55'
    }
    assert got_params == expect

    date_range = {'minute': 10}
    now = datetime.datetime(2011, 2, 14, 0, 0)
    params = DEFAULT_PARAMS.copy()
    got_params = kuzuha._gen_params_by_minute(date_range, now, params)
    expect = {
        'chk20110213.dat': 'checked',
        's1': '23',
        'e1': '50',
        's2': '24',
        'e2': '0'
    }
    assert got_params == expect


def test_gen_params():
    """lib.kuzuha.datetime.datetime.nowにパッチ当てられなかったから他はパス
    """
    actual = kuzuha.gen_params('', {'date': '20131014'})
    desired = DEFAULT_PARAMS_DETAIL.copy()
    desired.update({
        'kwd': '',
        'chk20131014.dat': 'checked',
        'k': 'あ'
    })
    assert actual == desired


def test__parse_keyword():
    actual = kuzuha._parse_keyword('マミ', 'cp932')
    assert actual == 'マミ'.encode('cp932')
    actual = kuzuha._parse_keyword(['マミ', 'パイ'], 'utf8')
    assert actual == 'マミ パイ'.encode('utf8')

def test__get_qwerty_log():
    pass


def test__get_gikogicom_log():
    pass


@nottest
def test__get_usamin_log():
    pass


@nottest
def test_get_log():
    pass


@nottest
def test_cleansing():
    pass


@nottest
def test_get_log_as_dict():
    pass
