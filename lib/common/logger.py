# -*- coding: utf-8 -*-
import logging
from logging import handlers
import sys


FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
DT_FMT = '%Y-%m-%d %H:%M:%S'
ROTATE_SETTING = {'backupCount': 30, 'when': 'midnight'}


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
