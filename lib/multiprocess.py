from __future__ import absolute_import
import functools
import multiprocessing.pool


def as_subprocess(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            pass
    return wrapper


class Pool(multiprocessing.pool.Pool):
    def _catch_keybord_interrupt(self, method, func, *args, **kwargs):
        try:
            return getattr(super(Pool, self), method)(func, *args, **kwargs)
        except KeyboardInterrupt:
            self.terminate()
            self.close()
            self.join()
            exit(130)

    def apply(self, func, args=(), kwds={}):
        return self._catch_keybord_interrupt(
            'apply', func, args=args, kwds=kwds)

    def apply_async(self, func, args=(), kwds={}, callback=None):
        return self._catch_keybord_interrupt(
            'apply_async', func, args, kwds, callback)

    def map(self, func, iterable, chunksize=None):
        return self._catch_keybord_interrupt(
            'map', func, iterable, chunksize=chunksize)

    def map_async(self, func, iterable, chunksize=None, callback=None):
        return self._catch_keybord_interrupt(
            'map_async', func, iterable, chunksize=chunksize, callback=callback)

    def imap(self, func, iterable, chunksize=1):
        return self._catch_keybord_interrupt(
            'imap', func, iterable, chunksize=chunksize)

    def imap_unordered(self, func, iterable, chunksize=1):
        return self._catch_keybord_interrupt(
            'imap_unordered', func, iterable, chunksize=chunksize)

class Test:
    def __init__(self):
        self.y = 0

    def fuga(self, x):
        return x*x+self.y

    def hoge(self):
        p = Pool(8)
        for i in p.imap_unordered(self.fuga, range(1000)):
            print(i)

if __name__ == "__main__":
    test = Test()
    test.hoge()
