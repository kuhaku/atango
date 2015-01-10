# -*- coding: utf-8 -*-
from lib import normalize
from lib.dialogue import qa, dialogue_search, misc
from lib.logger import logger
from job import reply


class TimeLineReply(reply.Reply):

    def make_response(self, text, screen_name=None, user='貴殿'):
        text = normalize.normalize(text)
        METHODS = (
            misc.respond_by_rule,
            qa.respond_oshiete,  # XXXって何? -> XXXは***
            qa.respond_what_who,  # (誰|何)がXXX? -> ***がXXX
            dialogue_search.respond,  # past post as-is
        )
        for method in METHODS:
            response = method(text)
            if response:
                break
        if not response:
            return
        if isinstance(response, str):
            response = {'text': response}
        response['text'] = self.replace_name(response['text'], screen_name, user)
        return response

    def respond(self, tweet):
        text = tweet['text']
        text = self.normalize(text)
        screen_name = tweet['user']['screen_name']
        name = tweet['user']['name']
        logger.debug('{id} {user[screen_name]} {text} {created_at}'.format(**tweet))
        (valid, reason) = self.is_valid_tweet(tweet)
        if not valid:
            logger.debug('skip because this tweet %s' % reason)
            return
        response = self.make_response(text, screen_name, name)
        if response and response.get('text'):
            response['text'] = '@%s ' % screen_name + response['text']
            response['id'] = tweet['id']
            return response
