# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import re
from elasticsearch import Elasticsearch
from lib.logger import logger
from . import swjson, web, normalize, file_io

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
    'kwd': '',
    'ao': 'o',
    'tt': 'a',
    'alp': 'checked',
    'g': 'checked',
    'm': 'g',
    'k': '%82%A0',
    'sv': 'on'
}
elasticsearch_setting = file_io.read('atango.json')['elasticsearch']


def _gen_params_by_day(date_range, now, params):
    '''
    Generate Kuzuha-BBS parameters by a range of days

    <dict<str>> date_range
    <datetime> now
    <dict<str>> params
    '''
    assert 0 <= date_range['day'] <= 6, ValueError

    for i in range(date_range['day'], -1, -1):
        dt = now - timedelta(i)
        idx = 'chk%d%02d%02d.dat' % (dt.year, dt.month, dt.day)
        params[idx] = 'checked'
    return params


def _gen_params_by_hour(date_range, now, params):
    '''
    Generate Kuzuha-BBS parameters by a range of hours

    <dict<str>> date_range
    <datetime> now
    <dict<str>> params
    '''
    dt = now - timedelta(hours=date_range['hour'])
    end_hour = 24 if dt.hour > now.hour else now.hour  # for when crossing days
    params.update({'s1': str(dt.hour), 's2': str(end_hour)})
    idx = 'chk%d%02d%02d.dat' % (dt.year, dt.month, dt.day)
    params[idx] = 'checked'
    return params


def _gen_params_by_minute(date_range, now, params):
    '''
    Generate Kuzuha-BBS parameters by a range of minutes

    <dict<str>> date_range
    <datetime> now
    <dict<str>> params
    '''
    start_dt = now - timedelta(minutes=date_range['minute'])
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
    '''
    Generate Kuzuha-BBS parameters by a range of times

    <dict<str>> date_range
    <datetime> now
    <dict<str>> params
    '''
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
    now = datetime.now()
    if date_range.get('date', None):
        idx = 'chk%s.dat' % (date_range['date'])
        params[idx] = 'checked'
    elif date_range.get('day', None):
        params.update(_gen_params_by_day(date_range, now, params))
    elif date_range.get('hour', None):
        params.update(_gen_params_by_hour(date_range, now, params))
    elif date_range.get('minute', None):
        params.update(_gen_params_by_minute(date_range, now, params))
    return params


def _parse_keyword(keyword, encoding):
    if isinstance(keyword, list):
        keyword = ' '.join(keyword)
    return keyword.encode(encoding)


def _get_qwerty_log(params):
    params['kwd'] = _parse_keyword(params['kwd'], 'cp932')
    html = web.open_url(QWERTY_URL, params=params)
    return html


def _get_gikogicom_log(params):
    if 'kwd' in params:
        params['qs'] = _parse_keyword(params['kwd'], 'cp932')
        del params['kwd']
    elif 'qs' in params:
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


def get_log_as_dict(site, params, fast=False, url=False, usamin_detail=False):
    parser = swjson.SwJson(fast=fast, url=url, usamin_detail=usamin_detail)
    html = get_log(site, params)
    if html:
        return parser.to_dict(html)


def build_date_filter(start_dt=None, end_dt=None):
    dt_range = {}
    if start_dt:
        dt_range['gte'] = start_dt.strftime('%Y-%m-%dT%H:%M:%S')
    if end_dt:
        dt_range['lte'] = end_dt.strftime('%Y-%m-%dT%H:%M:%S')
    return {'range': {'dt': dt_range}}


def build_date_filter_by_range(date_range={}, end_dt=datetime.now()):
    start_dt = end_dt - timedelta(**date_range)
    return build_date_filter(start_dt, end_dt)


def build_hour_filter(hours=1):
    now = datetime.now()
    hours_ago = now - timedelta(hours=hours)
    start_dt = datetime(hours_ago.year, hours_ago.month, hours_ago.day, hours_ago.hour, 0, 0)
    end_dt = datetime(hours_ago.year, hours_ago.month, hours_ago.day, hours_ago.hour, 59, 59)
    return build_date_filter(start_dt, end_dt)

def build_yesterday_filter():
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    start_dt = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    end_dt = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
    return build_date_filter(start_dt, end_dt)


def _build_sort(sort):
    sort_item = []
    for (field, order) in sort:
        if field in ('dt', '_score'):
            sort_item.append({field: {'order': order}})
        else:
            sort_item.append({
                '_script': {
                    'type': 'string',
                    'script': "doc['log.%s'].size()" % field,
                    'order': order
                }
            })
    return sort_item


def search(query='', field='q1', _operator='and', sort=[('_score', 'desc'), ('quoted_by', 'desc')],
           _filter={}, size=1000, _id=False):
    es = Elasticsearch([elasticsearch_setting])
    if query:
        es_query = {
            'match': {
                field: {
                    'query': query,
                    'operator': _operator,
                    'minimum_should_match': '85%'
                }
            }
        }
    else:
        es_query = {"match_all": {}}
    body = {
        "query": {
            "filtered": {
                "query": es_query,
                "filter": _filter
            }
        },
        'size': size
    }
    sort_item = _build_sort(sort)
    if sort_item:
        body.update({'sort': sort_item})
    logger.debug(body)
    result = es.search(index='qwerty', body=body, _source=True)
    if _id:
        return (x for x in result['hits']['hits'])
    return (x['_source'] for x in result['hits']['hits'])


def get_log_by_id(_id):
    es = Elasticsearch([elasticsearch_setting])
    return es.get(index='qwerty', id=_id)
