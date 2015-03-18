import functools
import time
from datetime import datetime
import mmh3


ELASTICSEARCH_DT_FORMAT = '%Y-%m-%dT%H:%M:%S'
KUZUHA_DT_FORMAT = '投稿日：%s/%02d/%02d(%s)%02d時%02d分%02d秒\n'
WEEKDAYS = '月火水木金土日'


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


def parse_log(log):
    body = ''
    if 'to' in log:
        body += '＞%s '% log['to']
    body += '　投稿者：%s 　'% log.get('author', '　')
    body += parse_kuzuha_date(log['dt'])
    for (i, idx) in enumerate(('q2', 'q1')):
        if idx in log:
            for line in log[idx].splitlines():
                body += '> ' * (2 - i) + line + '\n'
    body += '\n' + log.get('text')
    return body.strip()


def parse_time(response_timedelta):
    if 60 > response_timedelta:
        return '%d秒' % response_timedelta
    elif 3600 > response_timedelta:
        return '%d分%d秒' % divmod(response_timedelta, 60)
    (hours, minutes) = divmod(response_timedelta, 3600)
    (minutes, seconds) = divmod(minutes, 60)
    return '%d時間%d分%d秒' % (hours, minutes, seconds)


def compute_id(request):
    ua = request.headers.get('User-Agent', '')
    ip = request.remote_addr
    return mmh3.hash(ua + ip, 0)
