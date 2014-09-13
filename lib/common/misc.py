import numpy as np
from itertools import izip, imap


def choice(iterable):
    """
    Param:
        <iterable> iterable
    Return:
        <object> content
    """
    return iterable[np.random.randint(len(iterable))]


def nones(num, dimension=1):
    """
    Param:
        <int> num
    Return:
        <list> nones
    """
    if num < 1 or dimension < 1:
        raise ValueError('params must be more than 0')
    if dimension == 1:
        return [None for i in xrange(num)]
    elif dimension > 1:
        return [[None] * dimension for i in xrange(num)]
    elif not isinstance(num, int) or not isinstance(dimension, int):
        raise ValueError('params must be <int>')


def map_dict(method, d):
    """
    Apply method to dict's values
    Params:
        <callable> method
        <dict> d
    Return:
        <dict> d
    """
    return dict(izip(d.iterkeys(), imap(method, d.itervalues())))
