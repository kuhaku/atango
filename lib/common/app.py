# -*- coding: utf-8 -*-
import signal
import sys
import traceback
import re
import inspect
from .logger import Logger


TIME_LIMIT = 55


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
            return sys.exit(err_msg)
    return wrapper


class App(object):

    def __init__(self, verbose=False, debug=False):
        self.appname = self.__class__.__name__
        logger = Logger(self.appname, debug=debug)
        if verbose:
            logger.enable_stream_handler()
        self.verbose = verbose
        self.debug = debug
        self.logger = logger.logger
        self._decorate()

    def _decorate(self):
        """Decorate method by logger
        """
        for (name, method) in inspect.getmembers(self, inspect.ismethod):
            if not name.startswith('_'):
                setattr(self, name, decorator(self, method))
