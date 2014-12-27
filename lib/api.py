# -*- coding: utf-8 -*-
import re
import twitter
from cached_property import cached_property
from twitter.api import TwitterHTTPError
from . import file_io, misc
from .db import ShareableShelf

CFG_FILE = 'api.cfg'
re_photo_id = re.compile(r'<photoid>(?P<photoid>[0-9]+)</photoid>')


def __str__patch(self):
    fmt = ("." + self.format) if self.format else ""
    return ('%i %s%s %s using params: (%s)' % (self.e.code, self.uri, fmt,
                                               self.response_data, self.uriparts))

TwitterHTTPError.__str__ = __str__patch


class Twitter:

    def __init__(self):
        self.shelf = ShareableShelf('atango.shelf')        
        self.latest_tweets = self.shelf.get('latest_tweets', [])

    @cached_property
    def api(self):
        twitter_config = file_io.read(CFG_FILE)['Twitter']
        oauth = twitter.OAuth(twitter_config['access_token_key'],
                              twitter_config['access_token_secret'],
                              twitter_config['consumer_key'],
                              twitter_config['consumer_secret'])
        return twitter.Twitter(auth=oauth)

    def is_duplicate_tweet(self, tweet):
        if tweet in self.latest_tweets:
            return True
        if len(self.latest_tweets) > 10:
            self.latest_tweets.pop(0)
        self.latest_tweets.append(tweet)
        self.shelf['latest_tweets'] = self.latest_tweets
        return False


class Flickr:

    def __init__(self):
        config_parser = file_io.read(CFG_FILE)
        for idx in ('username', 'user_nsid', 'api_key', 'api_secret',
                    'oauth_token_key', 'oauth_token_secret'):
            setattr(self, idx, config_parser['Flickr'][idx])

    def upload(self, filename, title='', description='', tags=''):
        command = ['bash', '/work/atango/bin/flickr.sh']
        params = [title, description, tags, filename,
                  self.username, self.user_nsid, self.oauth_token_key,
                  self.oauth_token_secret, self.api_key, self.api_secret]
        result = misc.command(command + params, allow_err=False)
        match = re_photo_id.search(result[1])
        if match:
            return match.group('photoid')
        else:
            raise Exception("Didn't find flickr photoid in stdout:\n'%s'" % (result[1]))
