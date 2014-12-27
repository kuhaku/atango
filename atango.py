# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from lib.api import Twitter
from lib.db import ShareableShelf

class Atango(object):

    def __init__(self, verbose=False, debug=False):
        self.twitter = Twitter()
        self.verbose = verbose
        self.debug = debug

    def run(self, job):
        if job == 'wordcount':
            from job.wordcount.wordcount import WordCount
            up_flickr = not self.debug
            wc = WordCount(plot_wordmap=True, up_flickr=up_flickr,
                           verbose=self.verbose, debug=self.debug)
            self.twitter.post(wc.run(hour=1), debug=self.debug)
        elif job == 'url':
            from job.popular_url import PopularUrl
            pop_url = PopularUrl(verbose=self.verbose, debug=self.debug)
            for (i, message) in enumerate(pop_url.run(2), start=1):
                self.twitter.post(message, debug=self.debug)
                if i >= 3:
                    break
        elif job == 'ome':
            from job.ome import Ome
            ome = Ome(verbose=self.verbose, debug=self.debug)
            for message in ome.run(20):
                self.twitter.post(message, debug=self.debug)
        elif job == 'reply':
            from job.reply import Reply
            reply = Reply(verbose=self.verbose, debug=self.debug)
            for result in reply.run(count=10):
                self.twitter.post(result['text'], result['id'], result.get('media[]'),
                                  debug=self.debug)
                if not self.debug:
                    reply.update_latest_replied_id(result['id'])
        elif job == 'tl':
            from job.tl import TimeLineReply
            reply = TimeLineReply(verbose=self.verbose, debug=self.debug)
            result = reply.run(count=10)
            if result:
                self.twitter.post(result['text'], result['id'], result.get('media[]'),
                                  debug=self.debug)
                if not self.debug:
                    reply.update_latest_replied_id(result['id'])
        elif job == 'crawler':
            from job.crawler import Crawler
            crawler = Crawler(verbose=self.verbose, debug=self.debug)
            crawler.run()
        elif job == 'friends':
            friends = self.twitter.api.friends.ids(screen_name='sw_words', count=5000)
            shelf = ShareableShelf('twitter.shelf')
            shelf['friends'] = set(friends['ids'])
        elif job == 'cputemp':
            from job.cputemp import CpuTemperatureChecker
            temp_checker = CpuTemperatureChecker()
            message = temp_checker.run()
            if message:
                self.twitter.post(message, debug=self.debug)
        elif job == 'dialogue':
            from job.tl import TimeLineReply
            reply = TimeLineReply(verbose=self.verbose, debug=self.debug)
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
