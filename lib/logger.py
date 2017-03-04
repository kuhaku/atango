# -*- coding: utf-8 -*-
import logging
from logging import handlers
import sys
import random
import __main__

FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
DT_FMT = '%Y-%m-%d %H:%M:%S'
METHODS = 'addHandler setLevel debug info warn error critical propagate'
ROTATE_SETTING = {'backupCount': 30, 'when': 'midnight', 'encoding': 'utf8'}
CAPACITY = 10000
repeat = random.randint(0, 5)
TWEET_PREFIXES = (
    'んほぉおおおおおおお%sv(*´Д､ﾟ)v' % ('！' * repeat),
    'らめえぇぇぇぇぇぇ%sイっちゃううぅぅっv(*ﾟД､`)v' % ('♡' * repeat),
    'イっていい？イっていい？(*ﾟД､`)出すよ！',
    '死んじゃうぅぅぅぅ%sv(*ﾟД､`)v' % ('♡' * repeat),
    'ざんねん！　わたしの　ぼうけんは　これで　おわってしまった！',
    '中に出すよ？中に出すよ？(*ﾟД､`)イクっ！',
    'もうだめぇ(*ﾟД､`)イクイクイクイクイク！'
)


class TwitterHandler(handlers.BufferingHandler):
    def __init__(self, send_level=logging.CRITICAL):
        from lib import api
        self.twitter = api.Twitter()
        self.main_path = getattr(__main__, '__file__', 'UNKNOWN')
        self.send_level = send_level
        handlers.BufferingHandler.__init__(self, CAPACITY)

    def detect_max_level(self):
        max_level = logging.NOTSET
        for record in self.buffer:
            if record.levelno > max_level:
                max_level = record.levelno
        return max_level

    def has_send_level_log(self):
        return self.detect_max_level() >= self.send_level

    def format_message(self):
        error_message = []
        for record in self.buffer:
            if record.levelno >= self.send_level:
                error_message.append(record.msg)
        if error_message:
            message = '@kuhaku %s %s' % (random.choice(TWEET_PREFIXES), ''.join(error_message))
            if len(message) > 140:
                message = message[:139] + '…'
            return message

    def send(self):
        message = self.format_message()
        if message:
            self.twitter.api.statuses.update(status=message)

    def flush(self):
        if not self.main_path.endswith('nosetests'):
            self.send()
        self.buffer = []


class Logger(object):
    format = logging.Formatter(FORMAT, DT_FMT)

    def __init__(self, name=None, debug=False):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)
        self.logger.propagate = False

        self._delegate_methods('logger', METHODS.split())

    def enable_debug(self):
        self.logger.setLevel(logging.DEBUG)

    def disable_debug(self):
        self.logger.setLevel(logging.INFO)

    def _delegate_methods(self, attr, methods):
        for method_name in methods:
            method = getattr(getattr(self, attr), method_name)
            setattr(self, method_name, method)

    def set_propagate(self, val=True):
        self.logger.propagate = val

    def enable_stream_handler(self, stream=sys.stdout):
        handler = logging.StreamHandler(stream)
        handler.setFormatter(self.format)
        self.logger.addHandler(handler)

    def enable_file_handler(self, filename):
        handler = handlers.TimedRotatingFileHandler(filename, **ROTATE_SETTING)
        handler.setFormatter(self.format)
        self.logger.addHandler(handler)

    def enable_twitter_handler(self, debug=False):
        handler = TwitterHandler()
        self.logger.addHandler(handler)


logger = Logger('atango')
