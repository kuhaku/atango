# -*- coding: utf-8 -*-
import time
from collections import defaultdict, Counter
from itertools import combinations
import numpy as np
from lib import app, kuzuha, normalize, file_io, regex
from lib.distance import levenshtein
from lib.nlp import mecab, ngram
from . import wordmap
from .word import Word

SUTEGANA = tuple('ぁぃぅぇぉっゃゅょゎァィゥェォヵㇰヶㇱㇲッㇳㇴㇵㇶㇷㇹㇺャュョㇻㇼㇽㇾㇿヮ')


class WordCount(app.App):

    def __init__(self, plot_wordmap=True, up_flickr=False, verbose=False, debug=False):
        self.all_words = defaultdict(Word)
        self.start_time = 0
        self.plot_wordmap = plot_wordmap
        self.up_flickr = up_flickr
        self.ng_words = set(file_io.read('ng_words.txt'))
        super(WordCount, self).__init__(verbose, debug)

    def _get_log(self, hours=1):
        _filter = kuzuha.build_hour_filter(hours)
        self.start_hour = int(_filter['range']['dt']['gte'][11:13])
        self.end_hour = int(_filter['range']['dt']['lte'][11:13]) + 1
        return kuzuha.search(_filter=_filter)

    def compute_unixtime(self, posts):
        posts = list(posts)
        for (i, post) in enumerate(posts):
            posts[i]['time'] = int(time.mktime(time.strptime(post['dt'], '%Y-%m-%dT%H:%M:%S')))
        return posts

    @staticmethod
    def _sort_by_time(log):
        return sorted(log, key=lambda x: float(x['time']))

    @staticmethod
    def is_valid_post(post):
        if ('text' not in post) or post.get('author', '') == u'アニメ時報':
            return False
        return True

    @staticmethod
    def prepare_for_counting(text):
        text = regex.re_a_tag.sub('', text)
        text = normalize.normalize(text, emoticon=False, repeat=3)
        return text.splitlines()

    def count(self, text):
        text = self.prepare_for_counting(text)
        return mecab.count_doc(text)

    def calc_avg_time(self, word, post_time):
        word.time += (post_time - self.start_time)
        return word.time / word.count

    def merge_counter(self, counter, all_words, post_time=None):
        for word in counter.keys():
            all_words[word].surface = word
            all_words[word].count += 1
            all_words[word].distribution += counter
            if self.plot_wordmap:
                all_words[word].time = self.calc_avg_time(all_words[word],
                                                          post_time)
        return all_words

    def is_valid_word(self, word):
        if (word in self.ng_words or word.isnumeric() or word.startswith(SUTEGANA)):
            return False
        return True

    def del_word(self, word, all_words):
        del all_words[word]
        for w in all_words.keys():
            if word in all_words[w].distribution:
                del all_words[w].distribution[word]
        return all_words

    def cut_ngword(self, all_words):
        words = list(all_words.keys())
        for word in words:
            if not self.is_valid_word(word) and word in all_words:
                all_words = self.del_word(word, all_words)
        return all_words

    @staticmethod
    def sort_by_keys_length(mapping):
        return sorted(mapping.items(), key=lambda x: len(x[1].surface), reverse=True)

    def decrease_duplicate_count(self, all_words):
        for (key, val) in self.sort_by_keys_length(all_words):
            for ngrams in ngram.to_ngrams(key, len(key)):
                for n_gram in filter(lambda x: x in all_words, set(ngrams)):
                    if key == n_gram:
                        continue
                    elif val.count == all_words[n_gram].count:
                        all_words = self.del_word(n_gram, all_words)
                    #else:
                    #    all_words[key].count -= all_words[n_gram].count
        return all_words

    def del_minus_count_word(self, all_words):
        minus_words = [k for (k, v) in all_words.items() if v.count < 0]
        for word in minus_words:
            self.del_word(word, all_words)
        return all_words

    def del_duplicate_word(self, all_words):
        for (i, j) in combinations(all_words.keys(), 2):
            if len(i) != len(j):
                continue
            i, j = normalize.normalize_word(i), normalize.normalize_word(j)
            if levenshtein(i, j) == 0:
                if all_words[i].count > all_words[j].count:
                    big, small = i, j
                else:
                    big, small = j, i
                all_words[big].count += all_words[small].count
                self.del_word(small, all_words)
        return all_words

    def to_bag_of_words(self, all_words):
        idlist = dict(zip(all_words.keys(), range(len(all_words))))
        num_words = len(all_words)

        for (word, val) in all_words.items():
            total = sum(val.distribution.values())
            distribution = np.zeros(num_words)
            for (w, count) in val.distribution.items():
                distribution[idlist[w]] = count / total
            all_words[word].distribution = distribution
        return all_words

    def gen_report(self, all_words):
        message = u'%d~%d時の＠上海:\n' % (self.start_hour, self.end_hour)
        for word in sorted(all_words.values(),
                           key=lambda x: [x.count, len(x.surface)],
                           reverse=True):
            if len(message) + len(word.surface) + len(str(word.count)) + 1 < 116:
                if len(word.surface) > 1:
                    message = u'%s %s：%d,' % (message, word.surface, word.count)
            elif self.plot_wordmap:
                all_words = self.to_bag_of_words(all_words)
                wmap = wordmap.WordMap(upload_flickr=self.up_flickr, verbose=self.verbose,
                                       debug=self.debug)
                message = message[:-1]
                message += u' ' + wmap.run(all_words, message)
                return message
            else:
                break
        return message[:-1]

    def run(self, hour=1):
        log = self._get_log(hour)
        log = self.compute_unixtime(log)
        log = self._sort_by_time(filter(lambda x: 'time' in x, log))
        self.start_time = float(log[0]['time'])
        all_words = defaultdict(Word)

        for post in log:
            counter = Counter()
            if not self.is_valid_post(post):
                continue

            for index in ('text', 'q1'):
                if index in post and post[index]:
                    counter += self.count(post[index])
            all_words = self.merge_counter(counter, all_words, post['time'])

        all_words = self.cut_ngword(all_words)
        all_words = self.decrease_duplicate_count(all_words)
        all_words = self.del_minus_count_word(all_words)
        all_words = self.del_duplicate_word(all_words)
        return self.gen_report(all_words)


if __name__ == '__main__':
    wc = WordCount(plot_wordmap=True, up_flickr=False, verbose=True, debug=True)
    print(wc.run(hour=1))
