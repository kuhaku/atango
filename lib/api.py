# -*- coding: utf-8 -*-
import re
import base64
import os
import twitter
from twitter.api import TwitterHTTPError
from cached_property import cached_property
from . import file_io, misc, pathutil, normalize
from .db import redis
from .logger import logger

CFG_FILE = 'api.cfg'
re_photo_id = re.compile(r'<photoid>(?P<photoid>[0-9]+)</photoid>')
HALF_DAY = 60 * 60 * 12


def __str__patch(self):
    fmt = ("." + self.format) if self.format else ""
    return ('%i %s%s %s using params: (%s)' % (self.e.code, self.uri, fmt,
                                               self.response_data, self.uriparts))

TwitterHTTPError.__str__ = __str__patch


class Twitter(object):

    def __init__(self):
        cfg_dir = pathutil.cfgdir()
        self.replied_id_file = os.path.join(cfg_dir, 'latest_replied.txt')

    def _get_oauth(self):
        twitter_config = file_io.read(CFG_FILE)['Twitter']
        oauth = twitter.OAuth(twitter_config['access_token_key'],
                              twitter_config['access_token_secret'],
                              twitter_config['consumer_key'],
                              twitter_config['consumer_secret'])
        return oauth

    @cached_property
    def api(self):
        return twitter.Twitter(auth=self._get_oauth())

    @cached_property
    def stream_api(self):
        return twitter.TwitterStream(auth=self._get_oauth(), domain='userstream.twitter.com')

    def get_latest_replied_id(self):
        if not os.path.exists(self.replied_id_file):
            return 0
        with open(self.replied_id_file, 'r') as fd:
            return int(fd.readlines()[0].rstrip())

    def update_latest_replied_id(self, reply_id):
        with open(self.replied_id_file, 'w') as fd:
            fd.write(str(reply_id))

    def is_duplicate_tweet(self, tweet):
        key = 'tweet:%s' % tweet
        db = redis.db('twitter')
        if db.exists(key):
            db.expire(key, HALF_DAY)
            return True
        db.setex(key, 1, HALF_DAY)
        return False

    def post(self, text, reply_id=None, image=None, debug=False):
        if text:
            text = normalize.normalize(text, emoticon=True)
            params = {'status': text, 'in_reply_to_status_id': reply_id}
            logging_msg = 'Tweet: text={status}'
            if reply_id:
                logging_msg += ', id={in_reply_to_status_id}'
            logger.info(logging_msg.format(**params))
            if not debug:
                if self.is_duplicate_tweet(text):
                    logger.warn('tweet is duplicate: %s' % text)
                    return
                if image:
                    with open(image, "rb") as imagefile:
                        params["media[]"] = base64.b64encode(imagefile.read())
                        params["_base64"] = True
                    params['in_reply_to_status_id'] = str(reply_id)
                    self.api.statuses.update_with_media(**params)
                else:
                    self.api.statuses.update(**params)
        else:
            logger.warn('there is not string to output')


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
