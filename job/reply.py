# -*- coding: utf-8 -*-
import re
from lib import api, file_io, regex, normalize
from lib.logger import logger
from lib.dialogue import qa, dialogue_search, misc

re_screen_name = re.compile('@[\w]+[ 　]*')
re_atango = re.compile("[ぁあ]単語((ちゃん)|(先輩))?")


class Reply(object):

    def __init__(self):
        self.cfg = file_io.read('atango.json')['Reply']
        self.twitter = api.Twitter()

    def is_valid_tweet(self, mention):

        def is_ng_screen_name(screen_name):
            screen_name = screen_name.lower()
            return screen_name in self.cfg['NG_SCREEN_NAME']

        def is_ng_tweet(text):
            return any(word in text for word in self.cfg['NG_WORDS'])

        def is_ng_client(client):
            client = client.lower()
            return client in self.cfg['NG_CLIENT']

        reason = 'OK'
        if mention['id'] <= self.twitter.get_latest_replied_id():
            reason = 'is old'
        elif is_ng_screen_name(mention['user']['screen_name']):
            reason = 'is NG screen name'
        elif is_ng_tweet(mention['text']):
            reason = 'has NG word'
        elif is_ng_client(mention['source']):
            reason = 'is written by NG source'
        return (True, reason) if reason == 'OK' else (False, reason)

    def normalize(self, text):
        text = re_screen_name.sub('', text)
        text = re_atango.sub('貴殿', text)
        text = regex.re_url.sub('', text)
        text = text.strip()
        return text

    def replace_name(self, text, screen_name, name):
        if not screen_name:
            screen_name = name
        text = text.replace('\%sn', screen_name)
        text = text.replace('%name', name)
        return text

    def make_response(self, text, screen_name=None, user='貴殿'):
        text = normalize.normalize(text)
        METHODS = (
            qa.respond_oshiete,  # XXXって何? -> XXXは***
            qa.respond_what_who,  # (誰|何)がXXX? -> ***がXXX
            dialogue_search.respond,  # past post as-is
            misc.respond_by_rule,  # Rule-based response
            misc._random_choice,  # Randomly
        )
        for method in METHODS:
            logger.debug('execute %s' % method.__name__)
            response = method(text)
            if response:
                break
        if not response:
            response = {'text': 'ああ(;´Д`)'}
        if isinstance(response, str):
            response = {'text': response}
        response['text'] = self.replace_name(response['text'], screen_name, user)
        return response

    def respond(self, mention):
        text = self.normalize(mention['text'])
        screen_name = mention['user']['screen_name']
        name = mention['user']['name']
        logger.debug('{id} {user[screen_name]} {text} {created_at}'.format(**mention))
        (valid, reason) = self.is_valid_tweet(mention)
        if not valid:
            logger.debug('skip because this tweet %s' % reason)
            return
        response = self.make_response(text, screen_name, name)
        response['text'] = '@%s ' % screen_name + response['text']
        response['id'] = mention['id']
        return response
