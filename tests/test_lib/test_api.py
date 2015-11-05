# -*- coding: utf-8 -*-
import tempfile
import os
from nose.tools import assert_equals, assert_true, assert_raises
from collections import namedtuple
from unittest.mock import patch
from lib import api

FLICKR_CONFIG_IDX = ('username', 'user_nsid', 'api_key', 'api_secret', 'oauth_token_key',
                     'oauth_token_secret')
FLICKR_SH_TRUE_RETURN = ('<?xml version="1.0" encoding="utf-8" ?>\n'
                         '<rsp stat="ok">\n<photoid>92</photoid>\n</rsp>\n')
FLICKR_SH_FALSE_RETURN = ('<?xml version="1.0" encoding="utf-8" ?>\n'
                          '<rsp stat="ok">\n</rsp>\n')


class TwitterHTTPErrorMock(object):

    def __init__(self, format, code, uri, response_data, uriparts):
        self.format = format
        self.e = namedtuple('Error', 'code')(code)
        self.uri = uri
        self.response_data = response_data
        self.uriparts = uriparts


def test___str__patch():
    m = TwitterHTTPErrorMock('', 403, 'test.json', {'msg': 'hello'}, 'mamipai')
    setattr(m, '__str__', api.__str__patch)
    desired = '403 test.json {\'msg\': \'hello\'} using params: (mamipai)'
    assert m.__str__(m) == desired


class test_Twitter:

    def test___init__(self):
        config_patcher = patch('lib.api.file_io.read')
        config_mock = config_patcher.start()
        config_mock.return_value = {
            'Twitter': {
                'access_token_key': 0,
                'access_token_secret': 0,
                'consumer_key': 0,
                'consumer_secret': 0
            }
        }
        oauth_patcher = patch('lib.api.twitter.OAuth')
        oauth_mock = oauth_patcher.start()
        oauth_mock.return_value = None
        with patch('lib.api.twitter.Twitter') as twitter_mock:
            twitter_mock.return_value = True
            actual = api.Twitter()
            assert actual.api is True
        oauth_patcher.stop()
        config_patcher.stop()

    def test_get_latest_replied_id(self):
        twi = api.Twitter()
        twi.replied_id_file = '/this_is_no_existing_file/'
        assert twi.get_latest_replied_id() == 0

        twi.replied_id_file = tempfile.mkstemp()[1]
        with open(twi.replied_id_file, 'w') as fd:
            fd.write('100')
        try:
            assert twi.get_latest_replied_id() == 100
        finally:
            os.remove(twi.replied_id_file)

    def test_update_latest_replied_id(self):
        twi = api.Twitter()
        twi.replied_id_file = tempfile.mkstemp()[1]
        try:
            twi.update_latest_replied_id(1000)
            with open(twi.replied_id_file, 'r') as fd:
                assert fd.read() == '1000'
        finally:
            os.remove(twi.replied_id_file)


class test_Flickr:

    def test___init__(self):
        with patch('lib.api.file_io.read') as config_mock:
            config_mock.return_value = {
                'Flickr': {idx: 0 for idx in FLICKR_CONFIG_IDX}
            }
            actual = api.Flickr()
            for idx in FLICKR_CONFIG_IDX:
                assert hasattr(actual, idx) is True

    def test_upload(self):
        flickr = api.Flickr()
        with patch('lib.api.misc.command') as command_mock:
            command_mock.return_value = (True, FLICKR_SH_TRUE_RETURN, '')
            assert flickr.upload('/tmp/image.png') == '92'

            command_mock.return_value = (True, FLICKR_SH_FALSE_RETURN, '')
            assert_raises(Exception, flickr.upload, '/tmp/image.png')