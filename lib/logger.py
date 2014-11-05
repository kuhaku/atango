# -*- coding: utf-8 -*-
import logging
from logging import handlers
import sys
import random
import __main__
from lib.api import Twitter

FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
DT_FMT = '%Y-%m-%d %H:%M:%S'
ROTATE_SETTING = {'backupCount': 30, 'when': 'midnight'}
CAPACITY = 10000
repeat = random.randint(0, 5)
TWEET_PREFIXES = (
    'んほぉおおおおおおお%sv(*´Д､ﾟ)v' % ('！' * repeat),
    'らめえぇぇぇぇぇぇ%sイっちゃううぅぅっv(*ﾟД､`)v' % ('♡' * repeat),
    'イっていい？イっていい？(*ﾟД､`)出すよ！'
)


class TwitterHandler(handlers.BufferingHandler):

    def __init__(self, send_level=logging.CRITICAL, debug=False):
        self.twitter = Twitter()
        self.main_path = getattr(__main__, '__file__', 'UNKNOWN')
        self.send_level = send_level
        self.debug = debug
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
        error_message = [record.msg for record in self.buffer]
        message = '%s %s' % (random.choice(TWEET_PREFIXES), ''.join(error_message))
        if len(message) > 140:
            message = message[:139] + '…'
        return message

    def send(self):
        message = self.format_message()
        self.twitter.api.statuses.update(status=message)

    def flush(self):
        if (self.has_send_level_log() and not self.debug and
           not self.main_path.endswith('nosetests')):
            self.send()
        self.buffer = []


class Logger(object):

    def __init__(self, name=None, propagate=False, debug=False):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)
        self.logger.propagate = propagate
        self.format = logging.Formatter(FORMAT, DT_FMT)

    def enable_stream_handler(self, stream=sys.stdout):
        handler = logging.StreamHandler(stream)
        handler.setFormatter(self.format)
        self.logger.addHandler(handler)

    def enable_file_handler(self, filename):
        handler = handlers.TimedRotatingFileHandler(filename, **ROTATE_SETTING)
        handler.setFormatter(self.format)
        self.logger.addHandler(handler)

    def enable_twitter_handler(self):
        handler = TwitterHandler()
        self.logger.addHandler(handler)
