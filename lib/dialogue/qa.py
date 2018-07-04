# -*- coding: utf-8 -*-
"""Question Answering

This module responds to given question by log searching
"""
import re
from lib import kuzuha, normalize
from lib.nlp import mecab

re_oshiete = re.compile('(?P<query>.{1,15}[^っ])って[何誰]？')
NOUN_SUFFIXES = '(ちゃん)?(君)?(さん)?(先生)?'
NG_SUBSTRS = ('すか', 'ょうか', 'だろう', 'っていう', 'かなぁ', '?', '？', '2萌え')
NOT_FOUND_MESSAGE = 'ごめん(;´Д`)%s知らない'


def _extract_oshiete_answer(query, posts):
    for case_marking_particle in (u'って', u'は', u'の', ''):
        extract_rule = re.compile('(%s%s%s.{2,})' % (query, NOUN_SUFFIXES,
                                                     case_marking_particle))
        for post in posts:
            text = post['text']
            text = normalize.normalize(text.strip())
            if extract_rule.search(text):
                answer = extract_rule.search(text.strip()).group(1)
                if not answer or any(w in answer for w in NG_SUBSTRS):
                    continue
                if 3 < len(answer) < 120:
                    yield answer


def respond_oshiete(text, *args):
    oshiete_match = re_oshiete.search(text)
    if not oshiete_match:
        return None
    query = oshiete_match.group('query')
    posts = list(kuzuha.search(query, field='text', size=5))
    for answer in _extract_oshiete_answer(query, posts):
        yield answer
    yield NOT_FOUND_MESSAGE % query


def _build_what_who_query(text):
    IGNORE_POS = ('助詞,', '助動詞,', '記号,')
    query = ''
    m = mecab.MeCabWrapper()
    contains_what = False
    for node in m.parse_to_node(text):
        if node.surface:
            if node.prev.surface in ('何', '誰') and node.surface == 'が':
                contains_what = True
            elif contains_what:
                if any(pos in node.feature for pos in IGNORE_POS):
                    break
                query += node.surface
    return query


def respond_what_who(text, *args):
    """
    何がXXX？ -> YYYがXXX
    e.g. 何がおかしい？ -> 頭がおかしい
    """

    predicate = _build_what_who_query(text)
    if predicate:
        query = 'が%s は%s' % (predicate, predicate)
        for post in kuzuha.search(query, field='text', sort=[('dt', 'desc')], _operator='or', size=50):
            if 120 > len(post['text']) > 4 and not mecab.has_demonstrative(post['text']):
                yield post['text']
