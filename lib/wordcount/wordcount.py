# -*- coding: utf-8 -*-
from collections import defaultdict, Counter
from itertools import combinations, izip
import numpy as np

from common import app, kuzuha, normalize, config
from common.distance import levenshtein
from common.nlp import mecab, ngram
import wordmap
from word import Word


class WordCount(app.App):

    def __init__(self, plot_wordmap=True, up_flickr=False, verbose=False, debug=False):
        self.all_words = defaultdict(Word)
        self.start_time = 0
        self.plot_wordmap = plot_wordmap
        self.up_flickr = up_flickr
        self.ng_words = set(config.read('ng_words.txt'))
        super(WordCount, self).__init__(verbose, debug)

    def _get_log(self, keyword, date_range):
        kuzuha_params = kuzuha.gen_params(keyword, date_range=date_range)
        self.start_hour = kuzuha_params['s1']
        self.end_hour = kuzuha_params['s2']
        return kuzuha.get_log_as_dict("qwerty", kuzuha_params)

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
        text = normalize.normalize(text, emoticon=False, repeat=3)
        text = text.encode('utf8', 'replace')
        return text.splitlines()

    def count(self, text):
        text = self.prepare_for_counting(text)
        return mecab.count_doc(text)

    def calc_avg_time(self, word, post_time):
        word.time += (post_time - self.start_time)
        return word.time / word.count

    def merge_counter(self, counter, all_words, post_time=None):
        for word in counter.iterkeys():
            all_words[word].surface = word
            all_words[word].count += 1
            all_words[word].distribution += counter
            if self.plot_wordmap:
                all_words[word].time = self.calc_avg_time(all_words[word],
                                                          post_time)
        return all_words

    def is_valid_word(self, word):
        if (word in self.ng_words or word.isnumeric() or
           word.startswith((u'っ', u'ゃ', u'ゅ', u'ょ'))):
            return False
        return True

    def del_word(self, word, all_words):
        del all_words[word]
        for w in all_words.iterkeys():
            if word in all_words[w].distribution:
                del all_words[w].distribution[word]
        return all_words

    def cut_ngword(self, all_words):
        words = all_words.keys()
        for word in words:
            if not self.is_valid_word(word) and word in all_words:
                all_words = self.del_word(word, all_words)
        return all_words

    @staticmethod
    def sort_by_keys_length(mapping):
        return sorted(mapping.iteritems(), key=lambda x: len(x[1].surface), reverse=True)

    def decrease_duplicate_count(self, all_words):
        for (key, val) in self.sort_by_keys_length(all_words):
            for ngrams in ngram.to_ngrams(key, len(key)):
                for ng in filter(lambda x: x in all_words, set(ngrams)):
                    if key == ng:
                        continue
                    elif val.count == all_words[ng].count:
                        all_words = self.del_word(ng, all_words)
                    else:
                        all_words[key].count -= all_words[ng].count
        return all_words

    def del_duplicate_word(self, all_words):
        for (i, j) in combinations(all_words.iterkeys(), 2):
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
        idlist = dict(izip(all_words.keys(), xrange(len(all_words))))
        num_words = len(all_words)

        for (word, val) in all_words.iteritems():
            total = float(sum(val.distribution.itervalues()))
            distribution = np.zeros(num_words)
            for (w, count) in val.distribution.iteritems():
                distribution[idlist[w]] += count / total
            all_words[word].distribution = distribution
        return all_words

    def gen_report(self, all_words):
        message = u'%s~%s時の＠上海:\n' % (self.start_hour, self.end_hour)
        for word in sorted(all_words.itervalues(),
                           key=lambda x: [x.count, len(x.surface)],
                           reverse=True):
            if len(message) + len(word.surface) + len(str(word.count)) + 1 < 116:
                if len(word.surface) > 1:
                    message = u'%s %s：%d,' % (message, word.surface, word.count)
            elif self.plot_wordmap:
                all_words = self.to_bag_of_words(all_words)
                wmap = wordmap.WordMap(upload_flickr=self.up_flickr, verbose=self.verbose,
                                       debug=self.debug)
                message += u' ' + wmap.run(all_words, message[:-1])
                return message
            else:
                break
        return message[:-1]

    def run(self, keyword='', output=True, hour=1, day=False):
        log = self._get_log(keyword, {'hour': hour, 'day': day})
        log = self._sort_by_time(filter(lambda x: 'time' in x, log.itervalues()))
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
        all_words = self.del_duplicate_word(all_words)
        return self.gen_report(all_words)


if __name__ == '__main__':
    wc = WordCount(plot_wordmap=True, up_flickr=False, verbose=True, debug=True)
    print wc.run(output=True, hour=1)
