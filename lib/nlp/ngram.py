# -*- coding: utf-8 -*-
from itertools import zip_longest
from lib.multiprocess import Pool


class Ngramer(object):

    pool = None

    def set_pool(self):
        self.pool = Pool(4)

    def to_ngrams(self, item, max_n=0, min_n=2):
        if max_n < 1:
            max_n = len(item)
        args = zip_longest([item]*((max_n + 1) - min_n), range(min_n, max_n+1))
        if not self.pool:
            self.set_pool()
        return list(self.pool.imap(_to_ngram_unpack, args))
ngramer = Ngramer()
to_ngrams = ngramer.to_ngrams


def _to_ngram_unpack(arg):
    return to_ngram(arg[0], arg[1])


def to_ngram(item, n):
    return [item[i:i+n] for i in range(len(item) - n + 1)]
