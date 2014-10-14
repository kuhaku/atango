# -*- coding: utf-8 -*-
from itertools import product
from . import mathematics


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


def LCS(s1, s2):
    """
    Longest Common Subsequence
    """
    def extract_common_chars(a, b):
        ab_xor = set(a) ^ set(b)
        return (sorted(set(a) - ab_xor, key=a.index), sorted(set(b) - ab_xor, key=b.index))

    subseqs = []
    (s1, s2) = extract_common_chars(s1, s2)
    (lhs, rhs) = (s1, s2) if len(s1) < len(s2) else (s2, s1)
    for base in range(len(lhs)):
        for i in range(len(lhs[base:])):
            i += 1
            (subseq, j) = "", 0
            if base+i >= len(lhs):
                break
            start = rhs.index(lhs[base])
            for char in lhs[base:(base + i + 1)]:
                k = 0
                while start+j+k < len(rhs):
                    if rhs[start+j+k] == char:
                        subseq += char
                        j += k + 1
                        break
                    k += 1
            subseqs.append(subseq)
    subseqs = sorted(subseqs, key=lambda x: len(x))
    if len(subseqs) > 0:
        return subseqs[-1]
