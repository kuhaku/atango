# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from lib.common.app import App
from lib.common.api import Twitter


class Atango(App):

    def __init__(self, verbose=False, debug=False):
        if debug is False:
            self.twitter = Twitter()
        super(Atango, self).__init__(verbose, debug)

    def output(self, text):
        self.logger.info('Tweet: %s' % (text))
        if self.debug:
            return None
        if text:
            self.twitter.api.update_status(text)
            self.logger.info('Posting tweet is success')
        else:
            self.logger.warn('there is not string to output')

    def run(self, job):
        if job == 'wordcount':
            from lib.wordcount.wordcount import WordCount
            up_flickr = not self.debug
            wc = WordCount(plot_wordmap=True, up_flickr=up_flickr,
                           verbose=self.verbose, debug=self.debug)
            self.output(wc.run(hour=1))
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
