# -*- coding: utf-8 -*-
import datetime
from nose.tools import assert_equals
from lib import kuzuha


DEFAULT_PARAMS = {
    's1': '0',
    'e1': '0',
    's2': '24',
    'e2': '0'
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
    assert_equals(got_params, expect)


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
    assert_equals(got_params, expect)

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
    assert_equals(got_params, expect)


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
    assert_equals(got_params, expect)

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
    assert_equals(got_params, expect)
