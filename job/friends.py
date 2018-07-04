# -*- coding: utf-8 -*-
import json
import os
from lib.api import Twitter
from lib.pathutil import cfgdir


class TwitterFriendsUpdater(object):

    def __init__(self):
        self.twitter = Twitter()

    def run(self):
        friends = self.twitter.api.friends.ids(screen_name='sw_words',
                                               count=5000)
        with open(os.path.join(cfgdir(), 'friends.json'), 'w') as fd:
            json.dump(friends['ids'], fd)
