# -*- coding: utf-8 -*-
import shelve
import os
import time
from _gdbm import error
from . import path

ERRNO_35 = '[Errno 35] Resource temporarily unavailable'
WAIT_INTERVAL = 0.001

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

        self.decorate()

    def decorate(self):
        with shelve.open(**self.shelve_params) as db:
            for attr in dir(db):
                if not attr.startswith('__') and attr not in ('keys', 'values', 'items'):
                    setattr(self, attr, transaction(self, attr))
        for attr in ('keys', 'values', 'items'):
            setattr(self, attr, generator_as_list_transaction(self, attr))

    def __contains__(self, key):
        while True:
            try:
                with shelve.open(**self.shelve_params) as db:
                    return key in db
            except error as e:
                if str(e) == ERRNO_35:
                    time.sleep(WAIT_INTERVAL)
                    continue
                raise error(str(e))

    def __delitem__(self, key):
        while True:
            try:
                with shelve.open(**self.shelve_params) as db:
                    del db[key]
                    break
            except error as e:
                if str(e) == ERRNO_35:
                    time.sleep(WAIT_INTERVAL)
                    continue
                raise error(str(e))

    def __getitem__(self, key):
        while True:
            try:
                with shelve.open(**self.shelve_params) as db:
                    return db[key]
            except error as e:
                if str(e) == ERRNO_35:
                    time.sleep(WAIT_INTERVAL)
                    continue
                raise error(str(e))

    def __setitem__(self, key, val):
        while True:
            try:
                with shelve.open(**self.shelve_params) as db:
                    db[key] = val
                    break
            except error as e:
                if str(e) == ERRNO_35:
                    time.sleep(WAIT_INTERVAL)
                    continue
                raise error(str(e))
