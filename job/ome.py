# -*- coding: utf-8 -*-
import re
import itertools
from collections import defaultdict
import numpy as np
from lib import kuzuha, normalize, regex
from lib.distance import levenshtein, LCCS
from lib.nlp import mecab


re_kigou = re.compile('[\n\r！？!\?\.,…]')
THRESHOLD = 0.5
PREFIX = 'おめ？(;´Д`)'
HASH_TAG = '#おめ判定'
TWEET_LENGTH = 140
body_length = TWEET_LENGTH - len(PREFIX) - len(HASH_TAG)


class Ome(object):

    def __init__(self):
        self.synonym = normalize.SynonymUnification()

    @staticmethod
    def get_post_res_pairs(posts):
        def cleansing(s):
            return regex.re_a_tag.sub('', s.replace('\n', ''))
        pairs = defaultdict(list)
        for post in posts:
            if 'q1' in post and 'text' in post:
                text = cleansing(post['text'])
                parent = cleansing(post['q1'])
                pairs[parent].append(text)
        return pairs

    @staticmethod
    def simplify(text):
        text = normalize.remove_emoticon(text)
        return re_kigou.sub('', text)

    @staticmethod
    def levenshtein_per_char(pair):
        total_length = sum(map(len, pair))
        if total_length:
            return 1 - (levenshtein(*pair) / total_length)
        return 0

    @staticmethod
    def levenshtein_per_word(pair):
        nouns_pair = list(map(mecab.extract_word, pair))
        total_noun_length = sum(map(len, nouns_pair))
        if total_noun_length:
            return 1 - (levenshtein(*nouns_pair) / total_noun_length)
        return 0

    @staticmethod
    def levenshtein_per_char_yomi(pair):
        yomi_pair = list(map(mecab.to_yomi, pair))
        total_yomi_length = sum(map(len, yomi_pair))
        if total_yomi_length:
            return 1 - (levenshtein(*yomi_pair) / total_yomi_length)
        return 0

    def levenshtein_synonym_unify(self, pair):
        pair = list(map(self.synonym.unify, pair))
        total_length = sum(map(len, pair))
        if total_length:
            return 1 - (levenshtein(*pair) / total_length)
        return 0

    @staticmethod
    def lccs(pair):
        avg_length = sum(map(len, pair)) / 2
        lcs = LCCS(pair[0], pair[1], 2)
        if lcs:
            return len(lcs) / avg_length
        return 0

    def is_ome(self, text_a, text_b):
        measures = [self.levenshtein_per_char, self.levenshtein_per_word,
                    self.levenshtein_per_char_yomi, self.levenshtein_synonym_unify,
                    self.lccs]
        pair = list(map(self.simplify, [text_a, text_b]))
        scores = np.array([measure(pair) for measure in measures])
        result = sum(scores) / len(scores)
        if result >= THRESHOLD:
            return True
        return False

    @staticmethod
    def shorten(text, threshould=30, suffix='…'):
        if len(text) >= threshould:
            return text[:threshould - 1] + suffix
        return text

    def run(self, interval=20):
        posts = kuzuha.search('', _filter=kuzuha.build_date_filter_by_range({'minutes': interval}))
        pairs = self.get_post_res_pairs(posts)

        for (parent, responses) in pairs.items():
            if len(responses) > 1:
                ome_posts = set()
                for (lhs, rhs) in itertools.combinations(responses, 2):
                    if lhs and rhs and self.is_ome(lhs, rhs):
                        ome_posts |= {lhs, rhs}
                if len(ome_posts) > 1:
                    num_posts = len(ome_posts) + 1  # childs + parent
                    max_length = (body_length - num_posts*2) // num_posts
                    parent = self.shorten(parent, max_length)
                    message = '%s『%s』' % (PREFIX, parent)
                    for ome_post in ome_posts:
                        ome_post = self.shorten(ome_post, max_length)
                        message += '「%s」' % ome_post
                    message += HASH_TAG
                    yield message
