# -*- coding: utf-8 -*-
from itertools import product
from functools import reduce
import operator
from . import mathematics
from .nlp import ngram


def levenshtein(a, b, insert=1, delete=1, substitute=1):
    """
    Levenshtein edit distance
    Params:
        <Iterable> a
        <Iterable> b
        <int> insert : insertion cost
        <int> delete : deletion cost
        <int> substitute : substitution cost
    Return:
        <int> distance
    """
    len_a = len(a)
    len_b = len(b)
    d = mathematics.zeros((len_a + 1), (len_b + 1))

    for i in range(len_a + 1):
        d[i][0] = i * delete

    for j in range(len_b + 1):
        d[0][j] = j * insert

    for (i, j) in product(range(1, len_a + 1), range(1, len_b + 1)):
        x = 0 if a[i-1] == b[j-1] else substitute
        d[i][j] = min(d[i-1][j] + delete, d[i][j-1] + insert, d[i-1][j-1] + x)
    return d[-1][-1]


def LCCS(lhs, rhs, minimum_n):
    """
    Params:
        <str> lhs
        <str> rhs
        <int> minimum_n
    Return:
        <str> longest_contiguous_common_subsequence
    """
    if len(lhs) < minimum_n or len(rhs) < minimum_n:
        return None
    lhs = reduce(operator.add, (ngram.to_ngrams(lhs, minimum_n)))
    rhs = reduce(operator.add, (ngram.to_ngrams(rhs, minimum_n)))
    common_subsequences = set(lhs) & set(rhs)
    if common_subsequences:
        return sorted(common_subsequences, key=lambda x: len(x), reverse=True)[0]
