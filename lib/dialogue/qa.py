# -*- coding: utf-8 -*-
"""Question Answering

This module responds to given question by log searching
"""
import re
from lib import kuzuha, normalize
from lib.nlp import mecab

re_oshiete = re.compile('(?P<query>.*)((て)|(とは)|(について)|(のこと)|(を)|(には))(、)?([何誰]|(教えて)|(どこ)|(どう))')
re_xtsu = re.compile('っ$')
NOUN_SUFFIXES = '(ちゃん)?(君)?(さん)?(先生)?'
NG_SUBSTRS = ('すか', 'ょうか', 'だろう', 'っていう', 'かなぁ', '?', '？', '2萌え')
NOT_FOUND_MESSAGE = 'ごめん(;´Д`)%s知らない'


def _extract_oshiete_answer(query, posts, case_marking_particle):
    extract_rule = re.compile('(%s%s%s.{2,})' % (query, NOUN_SUFFIXES, case_marking_particle))

    for post in posts.values():
        text = post['text']
        text = normalize.normalize(text.strip())
        if extract_rule.search(text):
            answer = extract_rule.search(text.strip()).group(1)
            if not answer or len(answer) < 4 or any(w in answer for w in NG_SUBSTRS):
                continue
            return answer


def respond_oshiete(text):
    oshiete_match = re_oshiete.search(text)
    if not oshiete_match:
        return None
    query = oshiete_match.group('query')
    params = {'w': query}
    posts = kuzuha.get_log_as_dict('usamin', params)
    answer = None
    for case_marking_particle in (u'って', u'は', u'の', ''):
        answer = _extract_oshiete_answer(query, posts, case_marking_particle)
        if answer:
            break
    return answer if answer else NOT_FOUND_MESSAGE % query


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


def _extract_what_answer(substr, posts):
    for post in posts.values():
        post = post['text']
        if substr in post:
            if len(post) >= 4:
                return post


def respond_what_who(text):
    """
    何がXXX？ -> YYYがXXX
    e.g. 何がおかしい？ -> 頭がおかしい
    """

    query = _build_what_who_query(text)
    if query:
        params = {'w': query}
        posts = kuzuha.get_log_as_dict('usamin', params)
        if not posts:
            return None
        for particle in ('が', 'は'):
            answer = _extract_what_answer(particle + query, posts)
            if answer:
                return answer
