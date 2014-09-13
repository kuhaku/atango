# -*- coding: utf-8 -*-

def to_ngram(item, n):
    return [item[i:i+n] for i in xrange(len(item)-n+1)]
