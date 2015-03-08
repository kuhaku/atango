# -*- coding: utf-8 -*-
from lib import normalize
from lib.dialogue import qa, dialogue_search, misc
from lib.logger import logger
from job import reply

DEFAULT_USER = {'screen_name': 'kuhaku', 'name': '貴殿', 'replies': [], 'tweets': []}


class TimeLineReply(reply.Reply):

    def make_response(self, text, user_info=DEFAULT_USER):
        text = normalize.normalize(text)
        METHODS = (
            misc.respond_by_rule,
            qa.respond_oshiete,  # XXXって何? -> XXXは***
            qa.respond_what_who,  # (誰|何)がXXX? -> ***がXXX
            dialogue_search.respond,  # past post as-is
        )
        response = ''
        stop_make_response = False
        for method in METHODS:
            for response in method(text):
                response = response.strip()
                if response not in user_info['replies']:
                    stop_make_response = True
                    break
            if stop_make_response:
                break
        if not response:
            return
        if isinstance(response, str):
            response = {'text': response}
        response['text'] = self.replace_name(response['text'], user_info)
        return response

    def respond(self, tweet):
        text = tweet['text']
        text = self.normalize(text)
        logger.debug('{id} {user[screen_name]} {text} {created_at}'.format(**tweet))
        (valid, reason) = self.is_valid_tweet(tweet)
        if not valid:
            logger.debug('skip because this tweet %s' % reason)
            return
        user_info = self.get_userinfo(tweet)
        response = self.make_response(text, user_info)
        if response and response.get('text'):
            self.store_userinfo(user_info, tweet, response)
            response['text'] = '@%s ' % tweet['user']['screen_name'] + response['text']
            response['id'] = tweet['id']
            return response
