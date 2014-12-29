# -*- coding: utf-8 -*-
from collections import defaultdict
from itertools import chain
from lib import misc

BOS = '\x00'
EOS = '\x01'


class MarkovGenerater(object):

    def generate_markov_model(self, sequences):
        wordlist = list(chain.from_iterable(sequences))
        unique_words = sorted(set(wordlist), key=wordlist.index)
        markov_dict = defaultdict(list)
        for sequence in sequences:
            prev, interest = '', BOS
            for word in sequence + [EOS]:
                markov_dict[(prev, interest)].append(word)
                prev, interest = interest, word
        return (markov_dict, unique_words)

    def generate(self, words):
        (markov_dict, unique_words) = self.generate_markov_model(words)
        word_ids = defaultdict(lambda: len(word_ids))
        for x in unique_words:
            word_ids[x]

        sentence = ''
        (prev, interest)  = '', BOS
        word = ''
        while True:
            if not markov_dict[(prev, interest)]:
                (prev, interest)  = '', BOS
            word = misc.choice(markov_dict[(prev, interest)])
            prev, interest = interest, word
            if word == EOS and 20 < len(sentence) < 140:
                if sentence.count('(;´Д`)') == 2 and sentence[-6:] == '(;´Д`)':
                    sentence = sentence[:-6]
                return sentence
            elif len(sentence) > 120:
                sentence = ''
                (prev, interest)  = '', BOS
            elif word != BOS and word != EOS:
                sentence += unique_words[word_ids[word]].split(',')[0]
