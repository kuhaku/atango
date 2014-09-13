# -*- coding: utf-8 -*-
from nose.tools import assert_equals, assert_true
from datetime import datetime
from itertools import product
import numpy as np
from wordcount import wordmap, wordcount


class test_WordCount:

    def __init__(self):
        self.wm = wordmap.WordMap()

    def test_get_count_period(self):
        dt = datetime(2011, 2, 14, 1, 0)
        got = self.wm.get_count_period(dt)
        assert_equals(got, '0:00~1:00')
        dt = datetime(2011, 2, 14, 0, 0)
        got = self.wm.get_count_period(dt)
        assert_equals(got, '23:00~24:00')

    def test_generate_graphtitle(self):
        dt = datetime(2011, 2, 14, 1, 0)
        got = self.wm.generate_graphtitle(dt)
        assert_equals(got, '2011/2/14 0:00~1:00 qwerty')

    def test_sort_by_count(self):
        words = {
            'xx': wordcount.Word(surface='xx', count=2),
            'y': wordcount.Word(surface='y', count=2),
            'z': wordcount.Word(surface='z', count=1),
        }
        got = self.wm.sort_by_count(words)
        assert_equals(got[0].surface, 'xx')
        assert_equals(got[1].surface, 'y')
        assert_equals(got[2].surface, 'z')

    def test_measure_distance(self):
        words = [wordcount.Word(distribution=np.array([0, 0, 1]), time=20),
                 wordcount.Word(distribution=np.array([0, 1, 1]), time=30)]
        got = self.wm.measure_distance(words)
        assert_equals(got[0].distance[0], 0)
        assert_equals(got[0].distance[1], 5)
        assert_equals(got[1].distance[0], 5)

    def test_enhance_overlap_rate(self):
        label = {
            'x': {'min': 20, 'max': 100},
            'y': {'min': 0, 'max': 30}
        }
        got = self.wm.enhance_overlap_rate(label, [20, 5], 0.9)
        expect = {
            'x': {'min': 38, 'max': 82},
            'y': {'min': 4, 'max': 26}
        }
        assert_equals(got, expect)

    def test_has_overlap_position(self):
        label = {
            'x': {'min': 0, 'max': 2},
            'y': {'min': 0, 'max': 2}
        }
        canvas = np.ones((4, 4))
        assert_true(self.wm.has_overlap_position(canvas, label))
        canvas = np.zeros((4, 4))
        assert_true(not self.wm.has_overlap_position(canvas, label))
        canvas[0][0] = 1
        assert_true(self.wm.has_overlap_position(canvas, label))

    def test_eliminate_overwrap(self):
        label = {
            'x': {'min': 0, 'max': 2},
            'y': {'min': 0, 'max': 2}
        }
        canvas = np.zeros((100, 100))
        got = self.wm.eliminate_overwrap(canvas, label)
        assert_equals(got, label)
        canvas[0][0] = 1
        got = self.wm.eliminate_overwrap(canvas, label)
        assert_true(got['y'] == {'min': 1, 'max': 3} or
                    got['y'] == {'max': 2, 'min': 0})

    def test_put_label_on_canvas(self):
        canvas = np.zeros((4, 4))
        label = {
            'x': {'min': 0, 'max': 2},
            'y': {'min': 0, 'max': 2}
        }
        got = self.wm.put_label_on_canvas(canvas, label)
        for (i, j) in product(range(2), repeat=2):
            assert_true(got[i][j])
        assert_true(not got[0][3])
        assert_true(not got[3][3])

    def test_get_minmax(self):
        words = [wordcount.Word(x=0, y=0),
                 wordcount.Word(x=100, y=100)]
        got = self.wm.get_minmax(words)
        assert_equals(got['minx'], 0)
        assert_equals(got['maxx'], 100)
        assert_equals(got['miny'], 0)
        assert_equals(got['maxy'], 100)

    def test_rescale_canvas(self):
        words = [wordcount.Word(x=0, y=0),
                 wordcount.Word(x=1, y=1),
                 wordcount.Word(x=50, y=50),
                 wordcount.Word(x=100, y=100)]
        got = self.wm.rescale_canvas(words)
        assert_equals(got[0].x, 0)
        assert_equals(got[0].y, 0)
        assert_equals(got[1].x, 0.0095)
        assert_equals(got[1].y, 0.0095)
        assert_equals(got[2].x, 0.475)
        assert_equals(got[2].y, 0.475)
        assert_equals(got[3].x, 0.95)
        assert_equals(got[3].y, 0.95)
