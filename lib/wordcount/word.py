# -*- coding: utf-8 -*-
from collections import Counter


class Word:
    __slots__ = ('surface', 'count', 'distribution', 'distance', 'time', 'x', 'y')

    def __init__(self, **args):
        self.surface = args.get('surface', '')  # word surface
        self.count = args.get('count', 0)  # word frequency
        self.distribution = args.get('distribution', Counter())  # word frequency distribution
        self.distance = args.get('distance', None)  # smilarity distances between words
        self.time = args.get('time', 0)  # average time when word appeared
        self.x = args.get('x', 0)  # position x for generating word map
        self.y = args.get('y', 0)  # position y for generating word map
