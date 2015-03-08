# -*- coding: utf-8 -*-
import json
import re
from lib import api, file_io, regex, normalize
from lib.db import redis
from lib.logger import logger
from lib.dialogue import qa, dialogue_search, misc

re_screen_name = re.compile('@[\w]+[ 　]*')
re_atango = re.compile("[ぁあ]単語((ちゃん)|(先輩))?")
DEFAULT_USER = {'screen_name': 'kuhaku', 'name': '貴殿', 'replies': [], 'tweets': []}
ONE_WEEK = 60*60*24*7
TWO_WEEK = 60*60*24*14


class Reply(object):

    def __init__(self):
        self.cfg = file_io.read('atango.json')['Reply']
        self.twitter = api.Twitter()
        self.db = redis.db('twitter')
        global_context = self.db.get('global_context')
        if global_context:
            self.global_context = json.loads(global_context.decode('utf8'))
        else:
            self.global_context = []

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

    def get_userinfo(self, tweet):
        user_info = self.db.get('user:%s' % tweet['user']['id'])
        if user_info:
            user_info = json.loads(user_info.decode('utf8'))
            user_info['tweets'].append(tweet['text'])
        else:
            user_info = {'replies': [], 'tweets': [tweet['text']]}
        user_info.update({'screen_name': tweet['user']['screen_name'], 'name': tweet['user']['name']})
        return user_info

    def replace_name(self, text, user_info):
        text = text.replace('\%sn', user_info['screen_name'])
        text = text.replace('%name', user_info['name'])
        return text

    def make_response(self, text, user_info=DEFAULT_USER, global_context=[]):
        text = normalize.normalize(text)
        METHODS = (
            qa.respond_oshiete,  # XXXって何? -> XXXは***
            qa.respond_what_who,  # (誰|何)がXXX? -> ***がXXX
            dialogue_search.respond,  # past post as-is
            misc.respond_by_rule,  # Rule-based response
            misc._random_choice,  # Randomly
        )
        response = ''
        stop_make_response = False
        for method in METHODS:
            for response in method(text):
                response = response.strip()
                if not (response in user_info['replies'] or response in global_context):
                    stop_make_response = True
                    break
            if stop_make_response:
                break
        if not response:
            response = {'text': 'ああ(;´Д`)'}
        if isinstance(response, str):
            response = {'text': response}
        response['text'] = self.replace_name(response['text'], user_info)
        return response

    def store_userinfo(self, user_info, tweet, response):
        if len(user_info['replies']) >= 20:
            user_info['replies'].pop(0)
        if len(user_info['tweets']) >= 20:
            user_info['tweets'].pop(0)
        user_info['replies'].append(response['text'])
        key = 'user:%s' % tweet['user']['id']
        self.db.setex(key, json.dumps(user_info), TWO_WEEK)

    def respond(self, mention):
        mention['text'] = self.normalize(mention['text'])
        logger.debug('{id} {user[screen_name]} {text} {created_at}'.format(**mention))
        (valid, reason) = self.is_valid_tweet(mention)
        if not valid:
            logger.debug('skip because this tweet %s' % reason)
            return
        user_info = self.get_userinfo(mention)
        response = self.make_response(mention['text'], user_info, self.global_context)
        if len(self.global_context) > 100:
            self.global_context.pop(0)
        self.global_context.append(response)
        self.db.setex('global_context', json.dumps(self.global_context), ONE_WEEK)
        self.store_userinfo(user_info, mention, response)
        response['text'] = '@%s ' % mention['user']['screen_name'] + response['text']
        response['id'] = mention['id']
        return response
