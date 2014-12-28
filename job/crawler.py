# -*- coding: utf-8 -*-
import time
import signal
import numpy as np
from lib.logger import logger
from lib.api import Twitter
from lib import misc
from job.tl import TimeLineReply
from job.reply import Reply

TWO_MINUTES = 120
ONE_DAY = 60 * 60 * 24

class Crawler(object):
    def __init__(self, verbose=False, debug=False):
        self.tl_responder = TimeLineReply(verbose=verbose, debug=debug)
        self.reply_responder = Reply(verbose=verbose, debug=debug)
        self.twitter = Twitter()
        self.debug = debug
        signal.setitimer(signal.ITIMER_REAL, ONE_DAY)

    def is_duplicate_launch(self):
        result = misc.command('ps aux|grep crawler', True)
        logger.debug(result[1])
        ignore_grep = filter(lambda x: 'grep' not in x, result[1].splitlines())
        return len(list(ignore_grep)) > 2

    def respond(self, instance, tweet):
        response = instance.respond(tweet)
        if response:
            self.twitter.post(response['text'], response['id'], response.get('media[]'),
                              debug=self.debug)
            if not self.debug:
                self.tl_responder.update_latest_replied_id(response['id'])

    def is_valid_tweet(self, text):
        return not ('@' in text or '#' in text or 'RT' in text or 'http' in text)

    def run(self):
        if self.is_duplicate_launch():
            logger.warn('crawler is duplicate')
            return
        last_time = time.time()
        for tweet in self.twitter.stream_api.user():
            if 'text' in tweet:
                if tweet['text'].startswith('@sw_words'):
                    self.respond(self.reply_responder, tweet)
                elif np.random.randint(100) == 0 and self.is_valid_tweet(tweet['text']):
                    self.respond(self.tl_responder, tweet)
            if time.time() - last_time > TWO_MINUTES:
                mentions = self.twitter.api.statuses.mentions_timeline(count=200)
                for mention in mentions[::-1]:
                    self.respond(self.reply_responder, mention)
                last_time = time.time()
            signal.setitimer(signal.ITIMER_REAL, ONE_DAY)
