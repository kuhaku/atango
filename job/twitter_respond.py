# -*- coding: utf-8 -*-
import time
import numpy as np
from lib.logger import logger
from lib.api import Twitter
from lib import misc
from lib.db import redis
from job.tl import TimeLineReply
from job.reply import Reply

TWO_MINUTES = 120


class TwitterResponder(object):

    def __init__(self, debug=False):
        self.tl_responder = TimeLineReply()
        self.reply_responder = Reply()
        self.twitter = Twitter()
        self.db = redis.db('twitter')
        if not self.db.exists('latest_tl_replied'):
            self.db.set('latest_tl_replied', '(;´Д`)')
        self.debug = debug

    @staticmethod
    def is_duplicate_launch():
        result = misc.command('pgrep -fl python|grep "atango.py -j twitter_respond"', True)
        return bool(result[1].splitlines())

    def respond(self, instance, tweet, tl=False):
        response = instance.respond(tweet)
        if response:
            self.twitter.post(response['text'], response['id'], response.get('media[]'),
                              debug=self.debug)
            if not self.debug:
                self.twitter.update_latest_replied_id(response['id'])
                if tl:
                    self.db.set('latest_tl_replied', response['text'].split(' ')[0])

    def is_valid_tweet(self, text):
        return not ('@' in text or '#' in text or 'RT' in text or 'http' in text)

    def run(self):
        if self.is_duplicate_launch():
            logger.debug('TwitterResponder is already launched')
            return -1
        last_time = time.time()
        for tweet in self.twitter.stream_api.user():
            if 'text' in tweet:
                if tweet['text'].startswith('@sw_words'):
                    self.respond(self.reply_responder, tweet)
                elif (np.random.randint(100) < 2 and self.is_valid_tweet(tweet['text']) and
                      self.db.get('latest_tl_replied') != tweet['user']['screen_name']):
                    self.respond(self.tl_responder, tweet, tl=True)
            if time.time() - last_time > TWO_MINUTES:
                mentions = self.twitter.api.statuses.mentions_timeline(count=200)
                for mention in mentions[::-1]:
                    self.respond(self.reply_responder, mention)
                last_time = time.time()
