# -*- coding: utf-8 -*-
import numpy as np


def zeros(x, y=1):
    return [[0] * y for i in range(x)]


def to_safe_float(num):
    return float(str(num)[:10])


def mds(D):
    """
    Multi Dimensional Scaling
    Param:
        <numpy.array> D
    Return:
        <list<dict<str, float>>> positions
    """

    def calc_2D_positions(w1, w2, v, x1, x2, i):
        x = to_safe_float(w1 * v[i, x1].real)
        y = to_safe_float(w2 * v[i, x2].real)
        return {'x': x, 'y': y}

    N = len(D)
    S = D * D

    Q = np.eye(N) - np.ones((N, N)) / N

    P = -1.0 / 2 * Q * S * Q

    (w, v) = np.linalg.eig(P)
    ind = np.argsort(w)
    x1 = ind[-1]
    x2 = ind[-2]

    s = P.std(axis=0)
    w1 = s[x1].real
    w2 = s[x2].real

    return [calc_2D_positions(w1, w2, v, x1, x2, i) for i in range(N)]
