# -*- coding: utf-8 -*-
import os
import re
from lib import app, config, regex, normalize
from lib.dialogue import qa, dialogue_search, misc

re_screen_name = re.compile('@[\w]+[ 　]*')
re_atango = re.compile("[ぁあ]単語((ちゃん)|(先輩))")


class Reply(app.App):

    def __init__(self, verbose=False, debug=False):
        self.cfg = config.read('atango.json')['Reply']
        cfg_dir = config.cfgdir()
        self.replied_id_file = os.path.join(cfg_dir, 'latest_replied.txt')
        super(Reply, self).__init__(verbose, debug)

    def get_latest_replied_id(self):
        if not os.path.exists(self.replied_id_file):
            return 0
        with open(self.replied_id_file, 'r') as fd:
            return int(fd.readlines()[0].rstrip())

    def update_latest_replied_id(self, reply_id):
        with open(self.replied_id_file, 'w') as fd:
            fd.write(str(reply_id))

    def is_valid_mention(self, mention):

        def is_ng_screen_name(screen_name):
            return screen_name in self.cfg['NG_SCREEN_NAME']

        def is_ng_tweet(text):
            return any(word in text for word in self.cfg['NG_WORDS'])

        def is_ng_client(client):
            client = client.lower()
            return client in self.cfg['NG_CLIENT']

        if (mention['id'] <= self.get_latest_replied_id() or
           is_ng_screen_name(mention['user']['screen_name']) or
           is_ng_tweet(mention['text']),
           is_ng_client(mention['source'])):
            return False
        return True

    def normalize(self, text):
        text = re_screen_name.sub('', text)
        text = re_atango.sub('貴殿', text)
        text = regex.re_url.sub('', text)
        text = text.strip()
        return text

    def _replace_name(self, text, screen_name, name):
        if not screen_name:
            screen_name = name
        text = text.replace('\%sn', screen_name)
        text = text.replace('%name', name)
        return text

    def respond(self, text, screen_name=None, user='貴殿'):
        text = normalize.normalize(text)
        METHODS = (
            qa.respond_oshiete,  # XXXって何? -> XXXは***
            qa.respond_what_who,  # (誰|何)がXXX? -> ***がXXX
            dialogue_search.respond,  # past post as-is
            misc._random_choice,  # Randomly
        )
        for method in METHODS:
            response = method(text)
            if response:
                break
        if not response:
            response = 'ああ(;´Д`)'
        return self._replace_name(response, screen_name, user)

    def run(self, twitter_api, count=10):
        mentions = twitter_api.api.statuses.mentions_timeline(count=count)
        for mention in mentions[::-1]:
            text = self.normalize(mention['text'])
            screen_name = mention['user']['screen_name']
            name = mention['user']['name']
            if not self.is_valid_mention(mention):
                continue
            message = '@%s ' % screen_name
            message += self.respond(text, screen_name, name)
            yield message, mention['id']
            self.update_latest_replied_id(mention['id'])

if __name__ == '__main__':
    r = Reply()
    r.run()
