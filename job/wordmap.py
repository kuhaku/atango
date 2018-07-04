import sys
sys.path.append('/work/atango')
import tempfile
import glob
import os
from collections import defaultdict, Counter

import numpy as np
from scipy.spatial import distance
from scipy.sparse import csr_matrix
from sklearn import manifold
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from  matplotlib.offsetbox import AnchoredText
import PIL.ImageFont

from lib import api, app, kuzuha, normalize, file_io, regex
from lib.nlp import mecab

USAMIN_URL = 'http://usamin.mine.nu/cgi/swlog?b0=on&w='
NG_WORDS = ('人', '貴殿')


class WordMap(object):

    def __init__(self):
        self.word_counts = defaultdict(Counter)
        self.word_ids = defaultdict(lambda: len(self.word_ids))
        self.words = []
        self.unique_wordcounts = Counter()
        self.load_json()
        self.flickr = api.Flickr()
        self.temp_file = tempfile.mkstemp(suffix='.png')[1]


    def load_json(self):
        wordmap_conf = file_io.read('atango.json')['WordMap']
        self.font_path = wordmap_conf['font']
        self.bgcolor = wordmap_conf['bgcolor']
        self.fig_size = int(wordmap_conf['fig_size'])
        self.canvas_size = int(wordmap_conf['canvas_size'])
        self.overlap_allowable_rate = wordmap_conf['overlap_allowable_rate']
        self.min_font_size = wordmap_conf['min_font_size']

    @staticmethod
    def hide_unused_figure_object(ax):
        """
        図の目盛りやラベルを隠す
        """
        for tick in ax.yaxis.get_major_ticks() + ax.xaxis.get_major_ticks():
            tick.tick1On = False
            tick.label1On = False
            tick.tick2On = False

    def generate_graphtitle(self):
        """
        Return:
            <str> graphtitle
        """
        self.period = '%s:00~%s:00' % (self.start_hour, self.end_hour)
        graphtitle = '%s/%s/%s %s misao' % (self.year, self.month, self.day, self.period)
        return graphtitle

    def _configure_graph(self):
        plt.switch_backend('tkagg')
        plt.figure(figsize=(self.fig_size, self.fig_size))
        plt.axes(facecolor=self.bgcolor)
        ax = plt.gca()
        self.hide_unused_figure_object(ax)
        self.prop = font_manager.FontProperties(fname=self.font_path)

        self.graphtitle = self.generate_graphtitle()
        at = AnchoredText(self.graphtitle, loc=2, prop={'size': 10}, frameon=True)
        at.patch.set_boxstyle("round, pad=0., rounding_size=0.2")
        ax.add_artist(at)

        self.bbox = dict(boxstyle="round", ec=(1., 1., 1.), fc=(0., 0.27, 0.27))

    def _get_log(self, hours=1):
        _filter = kuzuha.build_hour_filter(hours)
        self.year = _filter['range']['dt']['gte'][0:4]
        self.month = _filter['range']['dt']['gte'][5:7]
        self.day = _filter['range']['dt']['gte'][8:10]
        self.start_hour = int(_filter['range']['dt']['gte'][11:13])
        self.end_hour = int(_filter['range']['dt']['lte'][11:13]) + 1
        return kuzuha.search(_filter=_filter, sort=[])

    @staticmethod
    def prepare_for_counting(text):
        text = regex.re_a_tag.sub('', text)
        text = normalize.normalize(text, emoticon=False, repeat=3)
        return text

    def count(self, log):
        for post in log:
            for idx in ('text', 'q1', 'q2'):
                if not post.get(idx):
                    continue
                if isinstance(post[idx], list):
                    post[idx] = '\n'.join(post[idx])
                for line in post[idx].splitlines():
                    line = self.prepare_for_counting(line)
                    for w in mecab.extract_word(line):
                        if w in NG_WORDS:
                            continue
                        ws = []
                        ws.append(self.word_ids[w])
                        if w not in self.words:
                            self.words.append(w)
                        cntr = Counter(ws)
                        for word in cntr.keys():
                            self.word_counts[word] += cntr
                        self.unique_wordcounts += cntr

    def to_array(self):
        maxim = len(self.word_ids)
        data = []
        indices = []
        indptr = [0]
        for (idx_word, cntr) in sorted(self.word_counts.items()):
            if self.unique_wordcounts[idx_word] < 3:
                indptr.append(len(data))
                continue
            for (word, count) in sorted(cntr.items()):
                indices.append(word)
                data.append(count)
            indptr.append(len(data))
        self.word_matrix = csr_matrix((data, indices, indptr), dtype=np.double)

    def analysis(self):
        Y = manifold.TSNE(n_components=2, init='pca').fit_transform(self.word_matrix.toarray())
        #Y = manifold.SpectralEmbedding().fit_transform(self.word_matrix.toarray())
        #Y = manifold.Isomap(30, 2).fit_transform(self.word_matrix.toarray())
        #Y = manifold.MDS().fit_transform(self.word_matrix.toarray())
        for (w, count) in self.unique_wordcounts.most_common()[::-1]:
            if count < 3 or w >= Y.shape[0]:
                Y[w] = np.array([0.5, 0.5])
        Y[:, 0] += abs(np.min(Y[:, 0]))
        Y[:, 0] /= np.max(Y[:, 0])
        Y[:, 1] += abs(np.min(Y[:, 1]))
        Y[:, 1] /= np.max(Y[:, 1])
        Y[np.where(Y < 0.5)] += 0.075
        Y[np.where(Y > 0.5)] -= 0.075
        self.Y = Y

    def plot(self):
        for (w, count) in self.unique_wordcounts.most_common()[::-1]:
            if count < 3 or w >= self.Y.shape[0]:
                continue
            args = {'size': count, 'color': 'white', 'ha': 'center', 'va': 'center',
                    'bbox': self.bbox, 'fontproperties': self.prop}
            plt.text(self.Y[w][0], self.Y[w][1], self.words[w], **args)
        plt.savefig(self.temp_file)

    def gen_report(self):
        message = '%d~%d時＠みさお:\n' % (self.start_hour, self.end_hour)
        for (w, count) in self.unique_wordcounts.most_common():
            if len(message) + len(self.words[w]) + len(str(count)) + 1 < 115:
                message += '%s：%d,' % (self.words[w], count)
        return message[:-1]

    def run(self, hour):
        log = self._get_log(hour)
        self._configure_graph()
        self.count(log)
        self.to_array()
        self.analysis()
        self.plot()
        return (self.gen_report(), self.temp_file)


if __name__ == '__main__':
    wm = WordMap()
    print(wm.run(1))
