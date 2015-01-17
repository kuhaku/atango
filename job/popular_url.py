# -*- coding: utf-8 -*-
import re
import os.path
from collections import Counter
import time
from bs4 import BeautifulSoup
from twitter.api import TwitterHTTPError
from lib import api, web, kuzuha, file_io, google_image, normalize
from lib.regex import re_url, re_html_tag
from lib.logger import logger

HOUR_RANGE = 4
MAX_TWEET_LENGTH = 140
SHORT_URL_LENGTH = 23
HASH_TAG = ' #上海人気URL'
DELIMITER = ' ／ '
TWEET_FORMAT = '%s %s %d件' + DELIMITER

re_title_delimiter = re.compile(u'[\[\(（【｜\)\]）】]|( \- )|( \| )|( ― )|( : )')
re_no_shortened_title = re.compile(u'「.+(｜|( \- )).+」')
image_extensions = ('.jpg', '.png', '.gif', '.jpg:large', '.png:large')
ignore_extensions = ('.zip', '.rar', '.swf', '.pdf', '.mp3', '.mp4')
cfg = file_io.read('popular_url.json')


class PopularUrl(object):

    def __init__(self, debug=False):
        self.twitter = api.Twitter()
        self.debug = debug

    def _count_url(self, posts):
        urls = Counter()
        for post in posts:
            for item in ('text', 'q1'):
                if not item in post:
                    continue
                text = re_html_tag.sub('', post[item])
                for url in set(re_url.findall(text)):
                    if any(ng in url for ng in cfg['IGNORE_URL']):
                        continue
                    urls[url] += 1
        return urls

    def _shorten_title(self, title):
        for substr in cfg['REMOVE_TITLE_SUBSTR']:
            title = title.replace(substr, '')
        title = re_url.sub('', title)
        title = title.replace(u'...', u'…')
        title = title.replace(' "', '"')
        if len(title) < 15 or re_no_shortened_title.search(title):
            return title
        titles = [substr for substr in re_title_delimiter.split(title)]
        titles = filter(lambda x: x, titles)  # 0文字の要素をカット
        return sorted(titles, key=lambda x: len(x), reverse=True)[0].strip()  # 最長の要素を返す

    def _get_title(self, url):
        title = ''
        root, ext = os.path.splitext(url)
        if ext in image_extensions:
            time.sleep(3)  # for avoiding to be treated as spam by Google
            logger.info('Search by google: %s' % url)
            results = google_image.search(url, best_kwds_max_length=18)
            keywords = filter(lambda x: not x.isdigit(), results['best_keywords'])
            title = ''.join(keywords)
        elif not ext in ignore_extensions:
            logger.info('Retrieve web resource: %s' % url)
            html = web.open_url(url)
            soup = BeautifulSoup(html)
            title = soup.title.string
            if title:
                title = normalize.htmlentity2unicode(title)
                title = self._shorten_title(title)
        return title

    @staticmethod
    def extract_tweet_id(url):
        url_parts = url.split('/')
        if len(url_parts) >= 6:
            return url_parts[5]
        return None

    @staticmethod
    def calc_tweet_length(tweet, title, count):
        actual_new_url_info_length = len(TWEET_FORMAT % (title, '*' * SHORT_URL_LENGTH, count))
        return len(tweet) + actual_new_url_info_length - len(DELIMITER)

    def run(self, hour_range=HOUR_RANGE):
        date_range = kuzuha.build_date_filter_by_range({'hours': hour_range})
        posts = kuzuha.search('http', _filter=date_range)
        tweet = ''
        for (url, count) in self._count_url(posts).most_common():
            if url.startswith('https://twitter.com/'):
                tweet_id = self.extract_tweet_id(url)
                if tweet_id:
                    logger.info('RT: id=%s (%s)' % (tweet_id, url))
                    if not self.debug:
                        try:
                            self.twitter.api.statuses.retweet(id=tweet_id)
                        except TwitterHTTPError as e:
                            logger.warn('%s %s' % (type(e), str(e)))
                    continue
            title = self._get_title(url)
            new_url_info = TWEET_FORMAT % (title, url, count)
            expected_length = self.calc_tweet_length(tweet, title, count)
            if expected_length < (MAX_TWEET_LENGTH - len(HASH_TAG)):
                tweet += new_url_info
            else:
                tweet = tweet[:-len(DELIMITER)] + HASH_TAG
                if tweet != HASH_TAG:
                    yield tweet
                tweet = new_url_info
        if tweet:
            if tweet.endswith(DELIMITER):
                tweet = tweet[:-len(DELIMITER)]
            yield tweet + HASH_TAG
