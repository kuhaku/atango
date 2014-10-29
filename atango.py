# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from lib.app import App
from lib.api import Twitter


class Atango(App):

    def __init__(self, verbose=False, debug=False):
        if debug is False:
            self.twitter = Twitter()
        super(Atango, self).__init__(verbose, debug)

    def output(self, text, reply_id=None):
        if text:
            if reply_id:
                self.logger.info('Tweet: text=%s, id=%d' % (text, reply_id))
                if not self.debug:
                    self.twitter.api.statuses.update(status=text, in_reply_to_status_id=reply_id)
            else:
                self.logger.info('Tweet: text=%s' % text)
                if not self.debug:
                    self.twitter.api.statuses.update(status=text)
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
            purl = PopularUrl(verbose=self.verbose, debug=self.debug)
            if self.debug:
                url_report_generator = purl.run(2)
            else:
                url_report_generator = purl.run(2, self.twitter)
            for (i, message) in enumerate(url_report_generator, start=1):
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
            for (message, reply_id) in reply.run(self.twitter, count=1):
                self.output(message, reply_id)
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
