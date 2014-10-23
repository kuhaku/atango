# -*- coding: utf-8 -*-
import signal
import sys
import traceback
import re
import os
import inspect
import random
from .logger import Logger


TIME_LIMIT = 55
ATANGO_DIR = '/work/atango/'
log_dir = os.path.join(ATANGO_DIR, 'logs')
DYING_MESSAGES = (
    'んほぉおおおおおおお%sv(*´Д､ﾟ)v' % ('！' * random.randint(0, 5)),
    'らめえぇぇぇぇぇぇ%sイっちゃううぅぅっv(*ﾟД､`)v' % ('♡' * random.randint(0, 5))
)


class Timeout(Exception):

    def __init__(self, reason='', response=None):
        self.reason = str(reason)
        self.response = response
        Exception.__init__(self, reason)


def decorator(self, function):
    def overtime_handler(*args):
        classname = self.__class__.__name__
        methodname = function.__name__
        message = 'exceeds %d seconds when executing %s.%s' % (TIME_LIMIT, classname, methodname)
        raise Timeout(message)

    def set_timer(timelimit):
        if signal.getitimer(signal.ITIMER_REAL)[0] == 0:
            signal.setitimer(signal.ITIMER_REAL, timelimit)
            signal.signal(signal.SIGALRM, overtime_handler)

    def dying_tweet():
        from .api import Twitter
        twitter = Twitter()
        dying_message = random.choice(DYING_MESSAGES)
        twitter.api.statuses.update(status=dying_message)

    def wrapper(*args, **kwargs):
        try:
            set_timer(TIME_LIMIT)
            return function(*args, **kwargs)
        except Exception as e:
            err_msg = '%s: %s' % (e.__class__.__name__, e)
            self.logger.critical(err_msg)
            tb = traceback.extract_tb(sys.exc_info()[2])
            trace = traceback.format_list(tb)
            self.logger.warn('---- traceback ----')
            for line in trace:
                text = re.sub(r'\n\s*', ' ', line.rstrip())
                self.logger.warn(text)
            self.logger.warn('-------------------')
            if not self.debug:
                dying_tweet()
            return sys.exit(err_msg)
    return wrapper


class App(object):

    def __init__(self, verbose=False, debug=False):
        self.appname = self.__class__.__name__
        self.filename = inspect.getfile(self.__class__)

        logger = Logger(self.appname, debug=debug)

        logpath = self._gen_logfile_path(self.filename)
        logger.enable_file_handler(logpath)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        if verbose:
            logger.enable_stream_handler()

        self.verbose = verbose
        self.debug = debug
        self.logger = logger.logger
        self._decorate()

    def _gen_logfile_path(self, filename):
        logfile_name = filename.replace(ATANGO_DIR, '').replace('/', '-')
        logfile_name += '.log'
        return os.path.join(log_dir, logfile_name)

    def _decorate(self):
        """Decorate method by logger
        """
        for (name, method) in inspect.getmembers(self, inspect.ismethod):
            if not name.startswith('_'):
                setattr(self, name, decorator(self, method))
