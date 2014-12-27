# -*- coding: utf-8 -*-
from lib import normalize
from lib.dialogue import qa, dialogue_search, misc
from job import reply


class TimeLineReply(reply.Reply):

    def respond(self, text, screen_name=None, user='貴殿'):
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

    def run(self, count=30):
        mentions = self.twitter.api.statuses.home_timeline(count=count)
        for mention in mentions[::-1]:
            text = mention['text']
            text = self.normalize(text)
            screen_name = mention['user']['screen_name']
            name = mention['user']['name']
            self.logger.debug('{id} {user[screen_name]} {text} {created_at}'.format(**mention))
            (valid, reason) = self.is_valid_mention(mention)
            if not valid:
                self.logger.debug('skip because this tweet %s' % reason)
                continue
            if '@' in text or '#' in text or 'RT' in text or 'http' in text:
                self.logger.debug('skip because this tweet has NG susbstr')
                continue
            response = self.respond(text, screen_name, name)
            if response and response.get('text'):
                response['text'] = '@%s ' % screen_name + response['text']
                response['id'] = mention['id']
                if not self.debug:
                    self.update_latest_replied_id(mention['id'])
                return response
