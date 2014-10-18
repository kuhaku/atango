# -*- coding: utf-8 -*-
import re
import twitter
from . import config, misc

CFG_FILE = 'api.cfg'
re_photo_id = re.compile(r'<photoid>(?P<photoid>[0-9]+)</photoid>')


class Twitter:

    def __init__(self):
        config_parser = config.read(CFG_FILE)
        oauth = twitter.OAuth(config_parser.get('Twitter', 'access_token_key'),
                              config_parser.get('Twitter', 'access_token_secret'),
                              config_parser.get('Twitter', 'consumer_key'),
                              config_parser.get('Twitter', 'consumer_secret'))
        self.api = twitter.Twitter(auth=oauth)


class Flickr:

    def __init__(self):
        config_parser = config.read(CFG_FILE)
        for idx in ('username', 'user_nsid', 'api_key', 'api_secret',
                    'oauth_token_key', 'oauth_token_secret'):
            setattr(self, idx, config_parser.get('Flickr', idx))

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
