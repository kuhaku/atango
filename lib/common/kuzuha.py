# -*- coding: utf-8 -*-
"""Library for KUZUHA BBS
"""

import urllib2
import datetime
import re
from . import swjson, web, normalize


# Regular Expressions
link_u = re.compile('<A[^<]+</A>')

QWERTY_URL = 'http://qwerty.on.arena.ne.jp/cgi-bin/bbs.cgi'
GIKOGICOM_URL = 'http://gikogi.com/bbslog/qwerty'
USAMIN_URL = 'http://usamin.mine.nu/cgi/swlog'

DEFAULT_KUZUHA_PARAMS = {
    's1': '0',
    'e1': '0',
    's2': '24',
    'e2': '0',
    'date': '',
    'kwd': '',
    'ao': 'o',
    'tt': 'a',
    'alp': 'checked',
    'g': 'checked',
    'm': 'g',
    'k': '%82%A0',
    'sv': 'on'
}


def _gen_params_by_day(date_range, now, params):
    """
    Generate Kuzuha-BBS parameters by a range of days

    <dict<str>> date_range
    <datetime> now
    <dict<str>> params
    """
    assert 0 <= date_range['day'] <= 6, ValueError

    for i in xrange(date_range['day'], -1, -1):
        dt = now - datetime.timedelta(i)
        idx = 'chk%d%02d%02d.dat' % (dt.year, dt.month, dt.day)
        params[idx] = 'checked'
    return params


def _gen_params_by_hour(date_range, now, params):
    """
    Generate Kuzuha-BBS parameters by a range of hours

    <dict<str>> date_range
    <datetime> now
    <dict<str>> params
    """
    dt = now - datetime.timedelta(hours=date_range['hour'])
    end_hour = 24 if dt.hour > now.hour else now.hour  # for when crossing days
    params.update({'s1': str(dt.hour), 's2': str(end_hour)})
    idx = 'chk%d%02d%02d.dat' % (dt.year, dt.month, dt.day)
    params[idx] = 'checked'
    return params


def _gen_params_by_minute(date_range, now, params):
    """
    Generate Kuzuha-BBS parameters by a range of minutes

    <dict<str>> date_range
    <datetime> now
    <dict<str>> params
    """
    start_dt = now - datetime.timedelta(minutes=date_range['minute'])
    params.update({
        's1': str(start_dt.hour),
        'e1': str(start_dt.minute),
        's2': str(now.hour),
        'e2': str(now.minute)})
    dt = now
    # when crossing days
    if (now.hour * 60 + now.minute) < (start_dt.hour * 60 + start_dt.minute):
        params.update({'s2': '24', 'e2': '0'})
        dt = start_dt
    idx = 'chk%d%02d%02d.dat' % (dt.year, dt.month, dt.day)
    params[idx] = 'checked'
    return params


def gen_params(kwd='', date_range={}):
    """
    Generate Kuzuha-BBS parameters by a range of times

    <dict<str>> date_range
    <datetime> now
    <dict<str>> params
    """
    if 'start_hour' not in date_range:
        date_range.update(
            {
                'start_hour': 0,
                'start_minute': 0,
                'end_hour': 24,
                'end_minute': 0
            }
        )
    params = DEFAULT_KUZUHA_PARAMS.copy()
    params.update({
        's1': str(date_range['start_hour']),
        'e1': str(date_range['start_minute']),
        's2': str(date_range['end_hour']),
        'e2': str(date_range['end_minute']),
        'kwd': kwd
    })
    now = datetime.datetime.now()
    if date_range.get('date', None):
        idx = 'chk%s.dat' % (date_range['date'])
        params[idx] = "checked"
    elif date_range.get('day', None):
        params = _gen_params_by_day(date_range, now, params)
    elif date_range.get('hour', None):
        params = _gen_params_by_hour(date_range, now, params)
    elif date_range.get('minute', None):
        params = _gen_params_by_minute(date_range, now, params)
    return params


def _parse_keyword(keyword, encoding):
    if isinstance(keyword, list):
        keyword = [urllib2.quote(x.encode(encoding, 'replace')) for x in keyword]
        return u'+'.join(keyword)
    else:
        return urllib2.quote(keyword.encode('cp932', 'replace'))


def _get_qwerty_log(params):
    params['kwd'] = _parse_keyword(params['kwd'], 'cp932')
    html = web.open_url(QWERTY_URL, params=params)
    return html


def _get_gikogicom_log(params):
    if 'kwd' in params:
        params['qs'] = _parse_keyword(params['kwd'], 'cp932')
        del params['kwd']
    else:
        params['qs'] = _parse_keyword(params['qs'], 'cp932')
    if 'n' not in params:
        params['n'] = 'all'
    if 'o' not in params:
        params['o'] = 'o'
    html = web.open_url(GIKOGICOM_URL, params=params)
    return html


def _get_usamin_log(params):
    if 'kwd' in params:
        params['w'] = _parse_keyword(params['kwd'], 'utf8')
        del params['kwd']
    else:
        params['w'] = _parse_keyword(params['w'], 'utf8')
    if 'ao' not in params:
        params['ao'] = 'a'
    if 'num' not in params:
        params['num'] = 100
    html = web.open_url(USAMIN_URL, params=params)
    return html


def get_log(site, params={}, link=False, font_tag=False):
    if site == 'qwerty':
        html = _get_qwerty_log(params)
        if '<PRE' not in html:
            return None
        html = cleansing(html, font_tag, link, site)

    elif site == 'gikogi':
        html = _get_gikogicom_log(params)
        if '<pre' not in html:
            return None
        html = cleansing(html, font_tag, link, site)

    elif site == 'usamin':
        html = _get_usamin_log(params)
        if html.count('<pre>') < 2:
            return None
        if link is False:
            html = link_u.sub('', html)
        html = normalize.normalize(html)
    return html


def cleansing(html, font_tag, link, site):
    html = normalize.normalize(html)
    html = html.replace('&gt;', '>')
    return html


def get_log_as_dict(site, params, fast=False, url=False):
    parser = swjson.SwJson(fast=fast, url=url)
    html = get_log(site, params)
    if html:
        return parser.to_dict(html)
