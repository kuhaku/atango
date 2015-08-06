# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from lib.api import Twitter
from lib.app import App


class Atango(App):

    def __init__(self, verbose=False, debug=False):
        self.twitter = Twitter()
        self.verbose = verbose
        self.debug = debug

    def run(self, job):
        self.setup_logger(job)
        if job == 'wordcount':
            from job.wordcount.wordcount import WordCount
            up_flickr = not self.debug
            wc = WordCount(plot_wordmap=True, up_flickr=up_flickr)
            self.twitter.post(self.execute(wc.run, hour=1), debug=self.debug)
        elif job == 'food':
            from job.clause_extractor import FoodExtractor
            e = FoodExtractor()
            self.twitter.post(self.execute(e.run, 24), debug=self.debug)
        elif job == 'okazu':
            from job.clause_extractor import OkazuExtractor
            e = OkazuExtractor()
            self.twitter.post(self.execute(e.run, 24), debug=self.debug)
        elif job == 'url':
            from job.popular_url import PopularUrl
            pop_url = PopularUrl(debug=self.debug)
            for (i, message) in enumerate(self.execute(pop_url.run, 2), start=1):
                self.twitter.post(message, debug=self.debug)
                if i >= 3:
                    break
        elif job == 'ome':
            from job.ome import Ome
            ome = Ome()
            for message in self.execute(ome.run, 20):
                self.twitter.post(message, debug=self.debug)
        elif job == 'summarize':
            from job.popular_post import PopularPost
            pp = PopularPost()
            result = self.execute(pp.run)
            self.twitter.post(result, debug=self.debug)
        elif job == 'markov':
            from job.markov import MarkovTweet
            mt = MarkovTweet()
            result = self.execute(mt.run, 60)
            self.twitter.post(result, debug=self.debug)
        elif job == 'twitter_respond':
            from job.twitter_respond import TwitterResponder
            crawler = TwitterResponder(debug=self.debug)
            crawler.run()
        elif job == 'elasticsearch_update':
            from elasticsearch_update import ElasticSearchUpdate
            updater = ElasticSearchUpdate()
            updater.run()
        elif job == 'cputemp':
            from job.cputemp import CpuTemperatureChecker
            temp_checker = CpuTemperatureChecker()
            message = temp_checker.run()
            if message:
                self.twitter.post(message, debug=self.debug)
        elif job == 'dialogue':
            from job.reply import Reply
            reply = Reply()
            tweet = {'id': 1 << 128, 'user': {'id': 0, 'name': 'まんこ', 'screen_name': 'manko'},
                     'created_at': '2015-03-09', 'source': 'm'}
            while True:
                tweet['text'] = input()
                print(reply.respond(tweet))
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
    atango.main(args.job.lower())
