# -*- coding: utf-8 -*-


def to_ngrams(item, max_n, min_n=2):
    return [to_ngram(item, n) for n in range(min_n, max_n + 1)]


def to_ngram(item, n):
    return [item[i:i+n] for i in range(len(item) - n + 1)]
