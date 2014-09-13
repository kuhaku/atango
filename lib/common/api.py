# -*- coding: utf-8 -*-
import tweepy
import flickrapi
from . import config, app


CFG_FILE = 'api.cfg'


class Twitter:

    def __init__(self):
        config_parser = config.read(CFG_FILE)
        auth = tweepy.OAuthHandler(config_parser.get('Twitter', 'consumer_key'),
                                   config_parser.get('Twitter', 'consumer_secret'))
        auth.set_access_token(config_parser.get('Twitter', 'access_token_key'),
                              config_parser.get('Twitter', 'access_token_secret'))
        self.api = tweepy.API(auth_handler=auth)


class Flickr(app.App):

    def __init__(self):
        super(Flickr, self).__init__()
        config_parser = config.read(CFG_FILE)
        self.api = flickrapi.FlickrAPI(config_parser.get('Flickr', 'api_key'),
                                  config_parser.get('Flickr', 'api_secret'))
        (token, frob) = self.api.get_token_part_one(perms='write')
        if not token:
            self.logger.warn('Flickr API requires an authorization')
            raw_input('Press ENTER after you authorized this program')
        self.api.get_token_part_two((token, frob))
