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
        elif job == 'markov':
            from job.markov import MarkovTweet
            mt = MarkovTweet()
            result = self.execute(mt.run, 60)
            self.twitter.post(result, debug=self.debug)
        elif job == 'crawler':
            from job.crawler import Crawler
            crawler = Crawler(debug=self.debug)
            crawler.run()
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
                print(reply.make_response(input(), '', ''))
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
