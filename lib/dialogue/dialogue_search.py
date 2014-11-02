# -*- coding: utf-8 -*-
from lib import normalize, swjson, regex, kuzuha, web
from lib.nlp import mecab

USAMIN_URL = 'http://usamin.mine.nu/cgi/swlog'


def _validate_query(query):
    validated_query = []
    for word in set(query):
        length = len(word)
        if length == 0:
            continue
        elif length == 1:
            word += '*'
        validated_query.append(word)
    return validated_query


def _is_valid_post(text):
    return len(text) < 125 and 'はい' != text


def _choice_res(html, words, or_flag):
    parser = swjson.SwJson()
    log = parser.to_dict(html, usamin_detail=False)
    for post in log.values():
        if 'q1' not in post or 'author' in post:
            continue
        post['q1'] = normalize.normalize(post['q1'])
        if or_flag:
            word_contains = any(word in post['q1'] for word in words)
        else:
            word_contains = all(word in post['q1'] for word in words)
        if word_contains:
            post['text'] = regex.re_a_tag.sub('', post['text'])
            if _is_valid_post(post['text']):
                return post['text']


def _extract_response_by_search(query, or_flag):
    validated_query = _validate_query(query)
    if not validated_query:
        return None
    and_or = 'o' if or_flag else 'a'
    params = {'b': 'qwerty', 'w': validated_query, 'rn': 'on', 'ao': and_or}
    posts = kuzuha.get_log_as_dict('usamin', params, usamin_detail=True)
    if not posts:
        return None
    for post in posts.values():
        if 'thread' in post:
            params = {'b': 'qwerty', 's': post['thread']}
            html = web.open_url(USAMIN_URL, params=params)
            response = _choice_res(html, query, or_flag=or_flag)
            if response:
                return response


def respond(text):
    """Extract a past post responding a post similar to given text
    """
    query = mecab.extract_word(text, 'content_word')
    response = _extract_response_by_search(query, False)
    if response:
        return response

    query = mecab.extract_word(text, 'noun')
    response = _extract_response_by_search(query, True)
    if response:
        return response
