# -*- coding: utf-8 -*-
from lib import regex, kuzuha
from lib.nlp import mecab
from lib.logger import logger

USAMIN_URL = 'http://usamin.mine.nu/cgi/swlog'


def _validate_query(query):
    validated_query = []
    for word in set(query):
        length = len(word)
        if length == 0:
            continue
        validated_query.append(word)
    return validated_query


def _validate_post(post):
    if 'author' in post:
        return False
    post['text'] = regex.re_a_tag.sub('', post['text'].rstrip())
    if len(post['text']) < 125 and 'はい' != post['text'] and 'はい(;´Д`)' != post['text']:
        logger.debug(post)
        return post['text']
    return False


def _extract_response_by_search(query, or_flag):
    validated_query = _validate_query(query)
    if not validated_query:
        return
    _operator = 'or' if or_flag else 'and'
    _filter = {
        "script" : {
            "script" : "doc['log.quoted_by'].size() > 0",
        }
    }
    posts = kuzuha.search(validated_query, _operator=_operator, _filter=_filter, size=200)
    for post in sorted(posts, key=lambda x: len(x['q1'])):
        if len(post['q1']) > 140:
            return
        response = _validate_post(post)
        if response:
            return response


def respond(text):
    """Extract a past post responding a post similar to given text
    """
    response = _extract_response_by_search([text], False)
    if response:
        return response

    query = mecab.extract_word(text, 'content_word')
    response = _extract_response_by_search([' '.join(query)], True)
    if response:
        return response

    query = mecab.extract_word(text, ('名詞,固有名詞',))
    response = _extract_response_by_search([' '.join(query)], True)
    if response:
        return response
