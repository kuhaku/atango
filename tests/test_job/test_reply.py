# -*- coding: utf-8 -*-
import tempfile
import os
from nose.tools import assert_equals, nottest
from job.reply import Reply


class test_Reply(object):

    def __init__(self):
        self.rep = Reply()

    def test_get_latest_replied_id(self):
        self.rep.replied_id_file = '/this_is_no_existing_file/'
        assert_equals(self.rep.get_latest_replied_id(), 0)

        self.rep.replied_id_file = tempfile.mkstemp()[1]
        with open(self.rep.replied_id_file, 'w') as fd:
            fd.write('100')
        try:
            assert_equals(self.rep.get_latest_replied_id(), 100)
        finally:
            os.remove(self.rep.replied_id_file)

    def test_update_latest_replied_id(self):
        self.rep.replied_id_file = tempfile.mkstemp()[1]
        try:
            self.rep.update_latest_replied_id(1000)
            with open(self.rep.replied_id_file, 'r') as fd:
                assert_equals(fd.read(), '1000')
        finally:
            os.remove(self.rep.replied_id_file)

    def test_is_valid_tweet(self):
        TWEET_MOCK = {
            'id': 0,
            'user': {'screen_name': ''},
            'text': '',
            'source': ''
        }
        tweet = TWEET_MOCK.copy()
        self.rep.get_latest_replied_id = lambda: 1
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
