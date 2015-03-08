# -*- coding: utf-8 -*-
import json
from unittest import mock
from nose.tools import assert_equals, nottest
from lib.db import redis
from job.reply import Reply


class test_Reply(object):

    def __init__(self):
        self.rep = Reply()

    def test_is_valid_tweet(self):
        TWEET_MOCK = {
            'id': 0,
            'user': {'screen_name': ''},
            'text': '',
            'source': ''
        }
        tweet = TWEET_MOCK.copy()
        with mock.patch('lib.api.Twitter.get_latest_replied_id') as m:
            m.return_value = 1
            assert_equals(self.rep.is_valid_tweet(tweet), (False, 'is old'))
            tweet['id'] = 2
            assert_equals(self.rep.is_valid_tweet(tweet), (True, 'OK'))

            tweet['user']['screen_name'] = 'sw_words'
            assert_equals(self.rep.is_valid_tweet(tweet), (False, 'is NG screen name'))

            tweet['user']['screen_name'] = ''
            tweet['text'] = 'レスしなくていい'
            assert_equals(self.rep.is_valid_tweet(tweet), (False, 'has NG word'))

            tweet['text'] = ''
            tweet['source'] = 'paper.li'
            assert_equals(self.rep.is_valid_tweet(tweet), (False, 'is written by NG source'))

    def test_normalize(self):
        tweet = '@sw_words ぁ単語は糞だな http://omanko'
        assert_equals(self.rep.normalize(tweet), '貴殿は糞だな')

    def test_replace_name(self):
        tweet = '<ENEMA>\%sn</ENEMA>'
        userinfo = {'screen_name': 'akari', 'name': '神岸あかり'}
        actual = self.rep.replace_name(tweet, userinfo)
        assert_equals(actual, '<ENEMA>akari</ENEMA>')

        tweet = '<ENEMA>%name</ENEMA>'
        actual = self.rep.replace_name(tweet, userinfo)
        assert_equals(actual, '<ENEMA>神岸あかり</ENEMA>')

    def test_get_userinfo(self):
        db = redis.db('twitter')
        db.delete('user:0')

        tweet = {'id': 0, 'user': {'id': 0, 'name': 'まんこ', 'screen_name': 'manko'},
                 'text': 'おまんこ', 'created_at': '2015-03-09', 'source': 'm'}
        actual = self.rep.get_userinfo(tweet)
        desired = {'name': 'まんこ', 'screen_name': 'manko', 'tweets': ['おまんこ'], 'replies': []}
        assert_equals(actual, desired)

        userinfo = {'name': 'まんこ', 'screen_name': 'manko',
                    'tweets': ['おまんこ', 'まんこ'], 'replies': ['manko', 'omanko']}
        db.set('user:0', json.dumps(userinfo))
        actual = self.rep.get_userinfo(tweet)
        userinfo['tweets'] = ['おまんこ', 'まんこ', 'おまんこ']
        assert_equals(actual, userinfo)

    @nottest
    def test_respond(self):
        pass

    @nottest
    def test_run(self):
        pass
