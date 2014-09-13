# -*- coding: utf-8 -*-
import logging
import sys


FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
DT_FMT = '%Y-%m-%d %H:%M:%S'


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
