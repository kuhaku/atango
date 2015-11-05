# -*- coding: utf-8 -*-
from nose.tools import assert_equals, assert_true, nottest, assert_almost_equal
from datetime import datetime
from itertools import product
import numpy as np
from scipy.spatial.distance import rogerstanimoto
from job.wordcount import wordmap, wordcount


class test_WordCount:

    def __init__(self):
        self.wm = wordmap.WordMap()

    @nottest
    def test_load_json(self):
        pass

    @nottest
    def test_hide_unused_figure_object(self):
        pass

    def test_get_count_period(self):
        dt = datetime(2011, 2, 14, 1, 0)
        got = self.wm.get_count_period(dt)
        assert got == '0:00~1:00'

        dt = datetime(2011, 2, 14, 0, 0)
        got = self.wm.get_count_period(dt)
        assert got == '23:00~24:00'

    def test_generate_graphtitle(self):
        dt = datetime(2011, 2, 14, 1, 0)
        got = self.wm.generate_graphtitle(dt)
        assert got == '2011/2/14 0:00~1:00 qwerty'

    @nottest
    def test_configure_graph(self):
        pass

    @nottest
    def test_determine_num_plot_items(self):
        pass

    def test_sort_by_count(self):
        words = {
            'xx': wordcount.Word(surface='xx', count=2),
            'y': wordcount.Word(surface='y', count=2),
            'z': wordcount.Word(surface='z', count=1),
        }
        got = self.wm.sort_by_count(words)
        assert got[0].surface == 'xx'
        assert got[1].surface == 'y'
        assert got[2].surface == 'z'

    def test_measure_distance(self):
        words = [wordcount.Word(distribution=np.array([0, 0, 1]), time=20),
                 wordcount.Word(distribution=np.array([0, 1, 1]), time=30)]
        got = self.wm.measure_distance(words)
        assert got[0].distance[0] == 0
        assert_almost_equal(got[0].distance[1], 0.502777, 5)
        assert_almost_equal(got[1].distance[0], 0.502777, 5)

    def test_calc_initial_position(self):
        input = (wordcount.Word(distance=np.array([1, 1, 1, 1])),
                 wordcount.Word(distance=np.array([1, 1, 1, 0])),
                 wordcount.Word(distance=np.array([0, 0, 0, 1])),
                 wordcount.Word(distance=np.array([0, 0, 1, 1])))
        got = self.wm.calc_initial_position(input)
        dist_zero_one = rogerstanimoto((got[0].x, got[0].y), (got[1].x, got[1].y))
        dist_zero_two = rogerstanimoto((got[0].x, got[0].y), (got[2].x, got[2].y))
        assert dist_zero_one < dist_zero_two is True

    def test_get_minmax(self):
        words = [wordcount.Word(x=0, y=0),
                 wordcount.Word(x=100, y=100)]
        got = self.wm.get_minmax(words)
        assert got['minx'] == 0
        assert got['maxx'] == 100
        assert got['miny'] == 0
        assert got['maxy'] == 100

    def test_rescale_canvas(self):
        words = [wordcount.Word(x=0, y=0),
                 wordcount.Word(x=1, y=1),
                 wordcount.Word(x=50, y=50),
                 wordcount.Word(x=100, y=100)]
        got = self.wm.rescale_canvas(words)
        assert got[0].x == 0
        assert got[0].y == 0
        assert got[1].x == 0.0095
        assert got[1].y == 0.0095
        assert got[2].x == 0.475
        assert got[2].y == 0.475
        assert got[3].x == 0.95
        assert got[3].y == 0.95

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
        assert got == expect

    def test_has_overlap_position(self):
        label = {
            'x': {'min': 0, 'max': 2},
            'y': {'min': 0, 'max': 2}
        }
        canvas = np.ones((4, 4))
        assert self.wm.has_overlap_position(canvas, label) is True
        canvas = np.zeros((4, 4))
        assert not self.wm.has_overlap_position(canvas, label) is True
        canvas[0][0] = 1
        assert self.wm.has_overlap_position(canvas, label) is True

    def test_eliminate_overwrap(self):
        label = {
            'x': {'min': 0, 'max': 2},
            'y': {'min': 0, 'max': 2}
        }
        canvas = np.zeros((100, 100))
        got = self.wm.eliminate_overwrap(canvas, label)
        assert got == label
        canvas[0][0] = 1
        got = self.wm.eliminate_overwrap(canvas, label)
        assert (got['y'] == {'min': 1, 'max': 3} or got['y'] == {'max': 2, 'min': 0})

    def test_put_label_on_canvas(self):
        canvas = np.zeros((4, 4))
        label = {
            'x': {'min': 0, 'max': 2},
            'y': {'min': 0, 'max': 2}
        }
        got = self.wm.put_label_on_canvas(canvas, label)
        for (i, j) in product(range(2), repeat=2):
            assert got[i][j] is True
        assert not got[0][3] is True
        assert not got[3][3] is True

    @nottest
    def test_arrange_word_position(self):
        pass

    @nottest
    def test_calc_label_size(self):
        pass

    @nottest
    def test_get_fontsize(self):
        pass

    @nottest
    def test_adjust_label(self):
        pass

    @nottest
    def test_plot_map(self):
        pass

    def test_add_search_link(self):
        message = '9~10時の＠上海:\n マミさん：36, まどマギ：18'
        expect = ('9~10時の＠上海: <a href="http://usamin.mine.nu/cgi/swlog?b0=on&w=マミさん">'
                  'マミさん</a>：36, <a href="http://usamin.mine.nu/cgi/swlog?b0=on&w=まどマギ">'
                  'まどマギ</a>：18')
        got = self.wm.add_search_link(message)
        assert got == expect

    @nottest
    def test_upload(self):
        pass

    @nottest
    def test_run(self):
        pass
