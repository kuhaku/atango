# -*- coding: utf-8 -*-
import re
from lib import web, kuzuha, normalize
from lib.nlp import cabocha
from lib.regex import re_url
from lib.logger import logger

MAX_TWEET_LENGTH = 140
re_right = re.compile('\).*')


class ClauseExtractor(object):

    def find_term(self, tokens, term):
        return any(term in token.feature for token in tokens)

    def find_clause(self, lemma, chunks, func):
        find_func = lambda idx: chunks[idx]['func'].surface == func

        for chunk in chunks:
            if not self.find_term(chunk['tokens'], lemma):
                continue
            if 'linked_by' not in chunk:
                continue
            if not any(find_func(idx) for idx in chunk['linked_by']):
                continue
            result = ''
            for idx in sorted(chunk['linked_by']):
                for token in chunks[idx]['tokens']:
                    result += token.surface
            for token in chunk['tokens']:
                result += token.surface
            return result

    def find(self, lemma, query, date_range):
        result = ''
        posts = kuzuha.search(query, field='text', _filter=date_range, sort=[])
        for post in posts:
            result = self.find_clause(lemma, cabocha.parse(post['text']), query[0])
            if result:
                result = re_right.sub(')', result)
                break
        return result or ''


class FoodExtractor(ClauseExtractor):
    def run(self, hour_range=24):
        date_range = kuzuha.build_date_filter_by_range({'hours': hour_range})
        result = self.find('飲む', 'を飲', date_range)
        result += self.find('食べる', 'を食', date_range)
        if len(result) < MAX_TWEET_LENGTH:
            return result


class OkazuExtractor(ClauseExtractor):
    def run(self, hour_range=24):
        date_range = kuzuha.build_date_filter_by_range({'hours': hour_range})
        result = self.find('しこる', 'でしこ', date_range)
        result += self.find('抜く', 'で抜', date_range)
        result += self.find('オナニュ', 'でオナニュす', date_range)
        result += self.find('オナニュ', 'でオナニュし', date_range)
        if len(result) < MAX_TWEET_LENGTH:
            return result
