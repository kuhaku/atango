import functools
import time
from datetime import datetime
import mmh3
from lib import kuzuha
from lib.logger import logger

ERROR_LOG_PATH = '/work/atango/logs/uwsgi_error.log'
ELASTICSEARCH_DT_FORMAT = '%Y-%m-%dT%H:%M:%S'
KUZUHA_DT_FORMAT = '%s/%02d/%02d(%s)%02d時%02d分%02d秒'
WEEKDAYS = '月火水木金土日'

SQUARE = '　 <a href="http://qwerty.on.arena.ne.jp/cgi-bin/bbs.cgi?m=f&u=&d=30&c=900&ff={}.dat&s={}">■</a>'
RHOMBUS = '　 <a href="http://qwerty.on.arena.ne.jp/cgi-bin/bbs.cgi?m=t&c=900&ff={}.dat&s={}">◆</a>'
SANKOU = '<a href="http://qwerty.on.arena.ne.jp/cgi-bin/bbs.cgi?m=f&u=&d=30&c=900&ff={}.dat&s={}">参考：{}</a>'


def catch_exception(f):
    @functools.wraps(f)
    def decorator(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.crit(e)
            #traceback.print_exception(file=open(ERROR_LOG_PATH, 'a+'))
    return decorator


def is_int_castable(s):
    if isinstance(s, int):
        return True
    if s.startswith('-'):
        s = s[1:]
    return s.isdigit()


def add_tag(text, tag, params={}):
    params_str = ''
    for (k, v) in params.items():
        params_str += '%s="%s"' % (k, v)
    if params_str:
        params_str = ' ' + params_str
    return '<%s%s>%s</%s>' % (tag, params_str, text, tag)


@functools.lru_cache()
def convert_datestr_to_datetime(dt_str):
    return datetime.strptime(dt_str, ELASTICSEARCH_DT_FORMAT)


def get_unixtime(dt_str):
    dt = convert_datestr_to_datetime(dt_str)
    return int(time.mktime(dt.timetuple()))


def parse_kuzuha_date(dt_str):
    dt = convert_datestr_to_datetime(dt_str)
    dt_str = KUZUHA_DT_FORMAT % (dt.year, dt.month, dt.day,
                                 WEEKDAYS[dt.weekday()],
                                 dt.hour, dt.minute, dt.second)
    return dt_str


def get_root_post_id(post_id):
    while True:
        post = kuzuha.get_log_by_id(post_id)
        if 'quote' not in post['_source']:
            break
        post_id = post['_source']['quote']
    return post['_id']


def dt_to_ymd(dt_str):
    return datetime.strftime(convert_datestr_to_datetime(dt_str), '%Y%m%d')


def add_res_button(post_id, dt):
    return SQUARE.format(dt, post_id)


def add_thread_button(post_id, dt):
    return RHOMBUS.format(dt, post_id)


def parse_log(log):
    if 'id' not in log:
        log['id'] = 0
    body = ''
    if 'quote' in log:
        body += '＞%s '% log.get('to', '　')
    body += '　投稿者：%s 　'% log.get('author', '　')

    body += '投稿日：'
    body += parse_kuzuha_date(log['dt'])

    dt = dt_to_ymd(log['dt'])
    body += add_res_button(log['id'], dt)

    thread_id = log['id']
    if 'quote' in log:
        thread_id = get_root_post_id(log['quote'])
    body += add_thread_button(thread_id, dt)

    body = add_tag(body, 'p')
    body += '\n<pre>'

    for (i, idx) in enumerate(('q2', 'q1')):
        if idx in log:
            if isinstance(log[idx], list):
                log[idx] = log[idx][0]
            for line in log[idx].splitlines():
                body += '> ' * (2 - i) + line + '\n'
    body += '\n' + log.get('text', '')

    if 'quote' in log:
        kuzuha_dt = kuzuha.get_log_by_id(log['quote'])['_source']['dt']
        dt = datetime.strftime(convert_datestr_to_datetime(kuzuha_dt), '%Y%m%d')
        body += '\n\n' + SANKOU.format(log['quote'], dt, parse_kuzuha_date(kuzuha_dt))
    return body.strip() + '</pre>'


def parse_time(response_timedelta):
    if 60 > response_timedelta:
        return '%d 秒' % response_timedelta
    elif 3600 > response_timedelta:
        return '%d 分 %d 秒' % divmod(response_timedelta, 60)
    (hours, minutes) = divmod(response_timedelta, 3600)
    (minutes, seconds) = divmod(minutes, 60)
    return '%d 時間 %d 分 %d 秒' % (hours, minutes, seconds)


def compute_id(request):
    ua = request.headers.get('User-Agent', '')
    ip = request.remote_addr
    return mmh3.hash(ua + ip, 0)
