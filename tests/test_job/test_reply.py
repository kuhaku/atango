# -*- coding: utf-8 -*-
from unittest import mock
from nose.tools import assert_equals, nottest
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
        screen_name = 'akari'
        name = '神岸あかり'
        actual = self.rep.replace_name(tweet, screen_name, name)
        assert_equals(actual, '<ENEMA>akari</ENEMA>')

        tweet = '<ENEMA>%name</ENEMA>'
        actual = self.rep.replace_name(tweet, screen_name, name)
        assert_equals(actual, '<ENEMA>神岸あかり</ENEMA>')

    @nottest
    def test_respond(self):
        pass

    @nottest
    def test_run(self):
        pass
