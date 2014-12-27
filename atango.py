# -*- coding: utf-8 -*-
from argparse import ArgumentParser
import base64
from lib.logger import logger
from lib.api import Twitter


class Atango(object):

    def __init__(self, verbose=False, debug=False):
        self.twitter = Twitter()
        self.verbose = verbose
        self.debug = debug

    def output(self, text, reply_id=None, image=None):
        if text:
            params = {'status': text, 'in_reply_to_status_id': reply_id}
            logging_msg = 'Tweet: text={status}'
            if reply_id:
                logging_msg += ', id={in_reply_to_status_id}'
            logger.info(logging_msg.format(**params))
            if not self.debug:
                if self.twitter.is_duplicate_tweet(text):
                    self.logger.warn('tweet is duplicate')
                    return
                if image:
                    with open(image, "rb") as imagefile:
                        params["media[]"] = base64.b64encode(imagefile.read())
                        params["_base64"] = True
                    params['in_reply_to_status_id'] = str(reply_id)
                    self.twitter.api.statuses.update_with_media(**params)
                else:
                    self.twitter.api.statuses.update(**params)
        else:
            self.logger.warn('there is not string to output')

    def run(self, job):
        if job == 'wordcount':
            from job.wordcount.wordcount import WordCount
            up_flickr = not self.debug
            wc = WordCount(plot_wordmap=True, up_flickr=up_flickr,
                           verbose=self.verbose, debug=self.debug)
            self.output(wc.run(hour=1))
        elif job == 'url':
            from job.popular_url import PopularUrl
            pop_url = PopularUrl(verbose=self.verbose, debug=self.debug)
            for (i, message) in enumerate(pop_url.run(2), start=1):
                self.output(message)
                if i >= 3:
                    break
        elif job == 'ome':
            from job.ome import Ome
            ome = Ome(verbose=self.verbose, debug=self.debug)
            for message in ome.run(20):
                self.output(message)
        elif job == 'reply':
            from job.reply import Reply
            reply = Reply(verbose=self.verbose, debug=self.debug)
            self.twitter = Twitter()
            for result in reply.run(count=10):
                self.output(result['text'], result['id'], result.get('media[]'))
                if not self.debug:
                    reply.update_latest_replied_id(result['id'])
        elif job == 'tl':
            from job.tl import TimeLineReply
            reply = TimeLineReply(verbose=self.verbose, debug=self.debug)
            self.twitter = Twitter()
            result = reply.run(count=10)
            if result:
                self.output(result['text'], result['id'], result.get('media[]'))
                if not self.debug:
                    reply.update_latest_replied_id(result['id'])
        elif job == 'cputemp':
            from job.cputemp import CpuTemperatureChecker
            temp_checker = CpuTemperatureChecker()
            message = temp_checker.run()
            if message:
                self.output(message)
        elif job == 'dialogue':
            from job.tl import Reply
            reply = Reply(verbose=self.verbose, debug=self.debug)
            while True:
                print(reply.respond(input()))
        else:
            raise ValueError('"%s" is not implemented yet' % job)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-j', '--job', type=str, required=True, help='job name')
    parser.add_argument('-v', '--verbose', help='output stdout', action='store_true',
                        default=False)
    parser.add_argument('-d', '--debug', help='dry-run and output detail info',
                        action='store_true', default=False)
    args = parser.parse_args()
    atango = Atango(args.verbose, args.debug)
    atango.run(args.job.lower())
