# -*- coding: utf-8 -*-
import functools
import subprocess
import time
import numpy as np
from lib.logger import logger


def command(cmd, shell=False, allow_err=False):
    '''
    Args:
        <tuple> command parameters
        <bool>  Popen shell option (default: False)
    Returns:
        (<bool> succeeded, <str> stdout, <str> stderr)
    '''
    out = ''
    error = ''
    proc = subprocess.Popen(cmd, shell=shell,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (out, error) = proc.communicate()
    (out, error) = (out.decode('utf8'), error.decode('utf8'))
    result = False if error else True
    if not allow_err and not result:
        message = 'Command: %s\nStdErr: %s' % (str(cmd), error)
        raise Exception(message)
    return (result, out, error)


def choice(iterable):
    """
    Param:
        <iterable> iterable
    Return:
        <object> content
    """
    np.random.seed(int(str(time.time())[-5:].replace('.', '')))
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
        return [None for i in range(num)]
    elif dimension > 1:
        return [[None] * dimension for i in range(num)]
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
    return dict(zip(d.keys(), map(method, d.values())))


def has_substr(iterable, substr):
    return any(substr in item for item in iterable)


def is_mojie(text):
    if '(  ' in text or '@@@@' in text:
        return True
    return text.count(' ') > 4


def retry(num=1, interval=0.1, allow_null=True):
    def receive_func(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(num):
                try:
                    result = func(*args, **kwargs)
                    assert result, ValueError('Null result is not allowed')
                    return result
                except Exception as e:
                    logger.warn('%s: %s' % (type(e), str(e)))
                    time.sleep(interval)
        return wrapper
    return receive_func
