# -*- coding: utf-8 -*-
from datetime import datetime
import os
import copy
import tempfile

import numpy as np
from scipy.spatial.distance import rogerstanimoto
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredText
import PIL.ImageFont

from lib import api, path, mathematics, app
from lib.misc import map_dict

USAMIN_URL = 'http://usamin.mine.nu/cgi/swlog?b0=on&w='
FLICKR_URL = 'https://www.flickr.com/photos/sw_words/'


class WordMap(app.App):

    def __init__(self, upload_flickr=False, verbose=False, debug=False):
        super(WordMap, self).__init__(verbose, debug)
        self.upload_flickr = upload_flickr
        if upload_flickr:
            self.flickr = api.Flickr()
            self.temp_file = tempfile.mkstemp(suffix='.png')[1]
        self.load_json()
        self.configure_graph()

    def load_json(self):
        wordmap_conf = path.read('atango.json')['WordMap']
        self.font_path = wordmap_conf['font']
        self.bgcolor = wordmap_conf['bgcolor']
        self.fig_size = wordmap_conf['fig_size']
        self.canvas_size = wordmap_conf['canvas_size']
        self.overlap_allowable_rate = wordmap_conf['overlap_allowable_rate']
        self.min_font_size = wordmap_conf['min_font_size']

    @staticmethod
    def hide_unused_figure_object(ax):
        u"""
        図の目盛りやラベルを隠す
        """
        for tick in ax.yaxis.get_major_ticks():
            tick.tick1On = False
            tick.label1On = False
            tick.tick2On = False
        for tick in ax.xaxis.get_major_ticks():
            tick.tick1On = False
            tick.label1On = False
            tick.tick2On = False

    @staticmethod
    def get_count_period(dt):
        """Get period of word count
        Param:
            <datetime> dt
        Return:
            <str> period of word count
        """
        if dt.hour == 0:
            return '%d:00~%d:00' % (23, 24)
        else:
            return '%d:00~%d:00' % (dt.hour - 1, dt.hour)

    def generate_graphtitle(self, dt):
        """
        Param:
            <datetime> dt
        Return:
            <str> graphtitle
        """
        self.period = self.get_count_period(dt)
        graphtitle = '%d/%d/%d %s qwerty' % (dt.year, dt.month, dt.day, self.period)
        return graphtitle

    def configure_graph(self):
        plt.switch_backend('agg')
        plt.figure(figsize=(self.fig_size, self.fig_size))
        plt.axes(axisbg=self.bgcolor)
        ax = plt.gca()
        self.hide_unused_figure_object(ax)
        self.prop = font_manager.FontProperties(fname=self.font_path)

        self.graphtitle = self.generate_graphtitle(datetime.now())
        at = AnchoredText(self.graphtitle, loc=2, prop={'size': 10}, frameon=True)
        at.patch.set_boxstyle("round, pad=0., rounding_size=0.2")
        ax.add_artist(at)

        self.bbox = dict(boxstyle="round", ec=(1., 1., 1.), fc=(0., 0.27, 0.27))

    @staticmethod
    def determine_num_plot_items(total_count):
        if total_count > 300:
            num_items = 50
        elif total_count > 250:
            num_items = 30
        elif total_count > 150:
            num_items = 20
        else:
            num_items = 10
        return num_items

    @staticmethod
    def sort_by_count(words):
        return sorted(words.values(), key=lambda x: [x.count, len(x.surface)],
                      reverse=True)

    @staticmethod
    def measure_distance(words):
        """
        distance = cos_similarity * time_distance
        """
        num_words = len(words)
        for i in range(num_words):
            words[i].distance = np.zeros(num_words)
            for j in range(num_words):
                cos_dist = rogerstanimoto(words[i].distribution, words[j].distribution)
                time_dist = np.abs(words[i].time - words[j].time)
                words[i].distance[j] = cos_dist * time_dist
        return words

    def calc_initial_position(self, words):
        """
        Calculate word label positions by MDS
        """
        D = np.array([word.distance for word in words])
        positions = mathematics.mds(D)
        self.logger.debug('initial positions by MDS are following:')
        for (i, position) in enumerate(positions):
            self.logger.debug('%s, %s, %s' % (words[i].surface, position['x'], position['y']))
            words[i].x = position['x']
            words[i].y = position['y']
        return words

    @staticmethod
    def get_minmax(words):
        all_x = [word.x for word in words]
        all_y = [word.y for word in words]
        minmax = {}
        minmax['minx'] = np.abs(min(all_x))
        minmax['maxx'] = np.abs(max(all_x))
        minmax['miny'] = np.abs(min(all_y))
        minmax['maxy'] = np.abs(max(all_y))
        return minmax

    def rescale_canvas(self, words):
        """
        Rescaling canvas by moving labels
        """
        minmax = self.get_minmax(words)
        xscale = 0.95 / (minmax['minx'] + minmax['maxx'])
        yscale = 0.95 / (minmax['miny'] + minmax['maxy'])
        for i in range(len(words)):
            words[i].x = (words[i].x + minmax['minx']) * xscale
            words[i].y = (words[i].y + minmax['miny']) * yscale
        return words

    @staticmethod
    def has_overlap_position(canvas, label):
        """
        Check whether the label position will overlap with other labels or not
        """
        return np.any(canvas[label['x']['min']:label['x']['max']:2,
                             label['y']['min']:label['y']['max']:2])

    @staticmethod
    def enhance_overlap_rate(label, item_sizes, overlap_allowable_rate):
        x_diff = int(item_sizes[0] * overlap_allowable_rate)
        y_diff = int(item_sizes[1] * overlap_allowable_rate)
        for (idx, val) in (('x', x_diff), ('y', y_diff)):
            label[idx]['min'] += val
            label[idx]['max'] -= val
        for idx in ('x', 'y'):
            if label[idx]['min'] < 0:
                label[idx]['max'] += label[idx]['min']
                label[idx]['min'] = 0
        return label

    def eliminate_overwrap(self, canvas, label):
        def move_axis(idx):
            if np.random.randint(2):
                if (label[idx]['max'] + distance) < self.canvas_size:
                    temp_label[idx]['min'] += distance
                    temp_label[idx]['max'] += distance
                elif (label[idx]['min'] - distance) > 0:
                    temp_label[idx]['min'] -= distance
                    temp_label[idx]['max'] -= distance
            else:
                if (label[idx]['min'] - distance) > 0:
                    temp_label[idx]['min'] -= distance
                    temp_label[idx]['max'] -= distance
                elif (label[idx]['max'] + distance) < self.canvas_size:
                    temp_label[idx]['min'] += distance
                    temp_label[idx]['max'] += distance

        temp_label = copy.deepcopy(label)
        distance = 1
        while self.has_overlap_position(canvas, temp_label):
            if np.random.randint(2):
                move_axis('x')
                if self.has_overlap_position(canvas, temp_label):
                    move_axis('y')
                else:
                    break
            else:
                move_axis('y')
                if self.has_overlap_position(canvas, temp_label):
                    move_axis('x')
                else:
                    break
            distance += 1
            if distance >= self.canvas_size:
                break
        return temp_label.copy()

    @staticmethod
    def put_label_on_canvas(canvas, label):
        canvas[label['x']['min']:label['x']['max'],
               label['y']['min']:label['y']['max']] = True
        return canvas

    def arrange_word_position(self, words):
        """
        Arrange word-label position to avoid overlaping with other labels
        """
        total_count = sum(map(lambda x: x.count, words))
        if total_count < 200:
            total_count = 200

        canvas = np.zeros([self.canvas_size, self.canvas_size], dtype=np.bool)
        for (n, word) in enumerate(words):
            font_size = self.calc_label_size(word.count, total_count)
            item_sizes = self.get_fontsize(font_size, word.surface)
            x = int(word.x * self.canvas_size)
            y = int(word.y * self.canvas_size)
            item_sizes /= 2.0
            label = {
                'x': {
                    'min': x - item_sizes[0],
                    'max': x + item_sizes[0]
                },
                'y': {
                    'min': y - item_sizes[1],
                    'max': y + item_sizes[1]
                }
            }
            # If label is over canvas, then move
            for idx in ('x', 'y'):
                if label[idx]['max'] >= self.canvas_size:
                    diff = (label[idx]['max'] - self.canvas_size)
                    label[idx]['max'] -= diff
                    label[idx]['min'] -= diff

            label = self.enhance_overlap_rate(label, item_sizes,
                                              self.overlap_allowable_rate)

            self.logger.debug('%s' % word.surface)
            self.logger.debug('%s' % label)
            label = self.eliminate_overwrap(canvas, label)

            self.logger.debug('%s' % label)
            for idx in ('x', 'y'):
                label[idx] = map_dict(int, label[idx])
            canvas = self.put_label_on_canvas(canvas, label)
            for idx in ('x', 'y'):
                avg = np.average((label[idx]['min'], label[idx]['max']))
                setattr(words[n], idx, avg / self.canvas_size)
        return words

    @staticmethod
    def calc_label_size(count, total_count):
        return (count + 10.0) / total_count * 700

    def get_fontsize(self, labelsize, word):
        font = PIL.ImageFont.truetype(self.font_path, int(labelsize))
        return np.array(font.getsize(word))

    def adjust_label(self, labelsize, word, x, y):
        """
        Adjust label position to avoid deviating from canvas
        """
        font_size = self.get_fontsize(labelsize, word)
        dist = np.array([x * self.canvas_size, y * self.canvas_size]) - (font_size / 2.0)
        if dist[0] < 0:
            x -= dist[0] / self.canvas_size - 0.001
        if dist[1] < 0:
            y -= dist[1] / self.canvas_size - 0.001
        return (x, y)

    def plot_map(self, words, total_count):
        """
        Plot word labels on word map
        """
        for word in words[::-1]:
            labelsize = self.calc_label_size(word.count, total_count)
            if word.count < 1 or labelsize < self.min_font_size:
                continue
            (x, y) = self.adjust_label(int(labelsize), word.surface, word.x, word.y)
            self.logger.debug('%s %f %f %s' % (word.surface, word.x, word.y, labelsize))
            args = {'size': labelsize, 'color': 'white', 'ha': 'center', 'va': 'center',
                    'bbox': self.bbox, 'fontproperties': self.prop}
            plt.text(word.x, word.y, word.surface, **args)

    @staticmethod
    def add_search_link(description):
        """
        Add word search link by Usamin to Flickr's description
        """
        items = description.split(' ')
        result = items[0][:-1]
        for item in [item.split('：') for item in items[1:]]:
            result += ' <a href="%s%s">%s</a>：%s' % (USAMIN_URL, item[0], item[0], item[1])
        return result#.encode('utf8', 'replace')

    def upload(self, description):
        """
        Upload wordmap image file to Flickr
        """
        plt.savefig(self.temp_file)
        photoid = self.flickr.upload(filename=self.temp_file,
                                     title=self.graphtitle,
                                     description=self.add_search_link(description),
                                     tags=self.period)
        os.remove(self.temp_file)
        url = FLICKR_URL + photoid
        return url

    def run(self, words, description=''):
        total_count = np.sum([v.count for v in words.values()])
        num_items = self.determine_num_plot_items(total_count)

        words = [w for w in self.sort_by_count(words) if len(w.surface) > 1][:num_items]
        words = self.measure_distance(words)
        words = self.calc_initial_position(words)
        words = self.rescale_canvas(words)
        words = self.arrange_word_position(words)
        words = self.rescale_canvas(words)

        self.plot_map(words, total_count)
        if self.upload_flickr is True:
            url = self.upload(description)
        else:
            #if os.getenv('DISPLAY'):
            #    plt.show()
            #else:
            temp_file = tempfile.mkstemp(suffix='.png')[1]
            plt.savefig(temp_file)
            self.logger.debug('word-map image is stored at %s' % temp_file)
            url = ''
        return url
