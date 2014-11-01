# -*- coding: utf-8 -*-
from lib import app, misc, normalize, swjson, regex, kuzuha, web
from lib.nlp import mecab


RESPONSES = (
    "ああ(;´Д`)",
    "ﾏｼﾞで？(;´Д`)",
    "ﾜﾗﾀ(;´Д`)",
    "何言ってるんだこの人(;´Д`)",
    "ﾔﾊﾞｲな(;´Д`)",
    "畏れ(;´Д`)",
    "わかってるよ(;´Д`)",
    "つーかまんこだろ"
)

USAMIN_URL = 'http://usamin.mine.nu/cgi/swlog'


class ResponseGenerator(app.App):

    def __init__(self, verbose=False, debug=False):
        self.parser = swjson.SwJson()
        super(ResponseGenerator, self).__init__(verbose, debug)

    @staticmethod
    def _random_choice(text=''):
        return misc.choice(RESPONSES)

    @staticmethod
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

    def _is_valid_post(self, text):
        return len(text) < 125 and 'はい' != text

    def _choice_res(self, html, words, or_flag):
        log = self.parser.to_dict(html, usamin_detail=False)
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
                if self._is_valid_post(post['text']):
                    return post['text']

    def _extract_response_by_search(self, query, or_flag):
        validated_query = self._validate_query(query)
        if not validated_query:
            return None
        and_or = 'o' if or_flag else 'a'
        params = {'b': 'qwerty', 'w': validated_query, 'rn': 'on', 'ao': and_or}
        self.logger.debug('Query: [%s]' % params)
        posts = kuzuha.get_log_as_dict('usamin', params, usamin_detail=True)
        if not posts:
            return None
        for post in posts.values():
            if 'thread' in post:
                params = {'b': 'qwerty', 's': post['thread']}
                self.logger.debug('Query: [%s]' % params)
                html = web.open_url(USAMIN_URL, params=params)
                response = self._choice_res(html, query, or_flag=or_flag)
                if response:
                    return response

    def _extract_response_from_log(self, text):
        """Extract a past post responding a post similar to given text
        """
        query = mecab.extract_word(text, 'content_word')
        response = self._extract_response_by_search(query, False)
        if response:
            return response

        query = mecab.extract_word(text, 'noun')
        response = self._extract_response_by_search(query, True)
        if response:
            return response            

    def _replace_name(self, text, screen_name, name):
        if not screen_name:
            screen_name = name
        text = text.replace('\%sn', screen_name)
        text = text.replace('%name', name)
        return text

    def respond(self, text, screen_name=None, user='貴殿'):
        text = normalize.normalize(text)
        METHODS = (
            self._extract_response_from_log,  # past post as-is
            self._random_choice,  # Randomly
        )
        for method in METHODS:
            response = method(text)
            if response:
                break
        if not response:
            response = 'ああ(;´Д`)'
        return self._replace_name(response, screen_name, user)
