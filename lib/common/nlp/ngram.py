# -*- coding: utf-8 -*-


def to_ngrams(item, max_n):
    return [to_ngram(item, n) for n in xrange(2, max_n + 1)]


def to_ngram(item, n):
    return [item[i:i+n] for i in xrange(len(item) - n + 1)]
