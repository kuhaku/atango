# -*- coding: utf-8 -*-
import shelve
import os
import time
from _gdbm import error
from . import path


ERRNO_35 = '[Errno 35] Resource temporarily unavailable'
WAIT_INTERVAL = 0.001
KEYS = ('cache', 'clear', 'close', 'dict', 'get', 'keyencoding', 'pop', 'popitem',
        'setdefault', 'sync', 'update', 'writeback')


def transaction(self, attr_name):
    def execute(*args, **kwargs):
        while True:
            try:
                with shelve.open(**self.shelve_params) as db:
                    method = getattr(db, attr_name)
                    return method(*args, **kwargs)
            except error as e:
                if str(e) == ERRNO_35:
                    time.sleep(WAIT_INTERVAL)
                    continue
                raise error(str(e))
    return execute


def generator_as_list_transaction(self, attr_name):
    def execute(*args, **kwargs):
        while True:
            try:
                with shelve.open(**self.shelve_params) as db:
                    method = getattr(db, attr_name)
                    return list(method(*args, **kwargs))
            except error as e:
                if str(e) == ERRNO_35:
                    time.sleep(WAIT_INTERVAL)
                    continue
                raise error(str(e))
    return execute


def decorate(cls):
    for attr in KEYS:
        setattr(cls, attr, transaction(cls, attr))
    for attr in ('keys', 'values', 'items'):
        setattr(cls, attr, generator_as_list_transaction(cls, attr))


class ShareableShelf(object):

    def __init__(self, filename='atango.shelve', flag='', protocol=None, writeback=False):
        filename = os.path.join(path.datadir(), filename)
        self.shelve_params = {'filename': filename}
        if flag:
            self.shelve_params['flag'] = flag
        else:
            self.shelve_params['flag'] = 'w' if os.path.exists(filename) else 'c'
        self.shelve_params['protocol'] = protocol
        self.shelve_params['writeback'] = writeback

        self = decorate(self)

    def __contains__(self, key):
        return transaction(self, '__contains__')(key)

    def __delitem__(self, key):
        return transaction(self, '__delitem__')(key)

    def __getitem__(self, key):
        return transaction(self, '__getitem__')(key)

    def __setitem__(self, key, val):
        return transaction(self, '__setitem__')(key, val)
