# -*- coding: utf-8 -*-
import re
import os.path
from collections import Counter
import time
from bs4 import BeautifulSoup
from lib import app, web, kuzuha, file_io, google_image, normalize
from lib.regex import re_url, re_title, re_html_tag

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


class PopularUrl(app.App):

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
        if re_no_shortened_title.search(title):
            return title
        titles = [substr for substr in re_title_delimiter.split(title)]
        titles = filter(lambda x: x, titles)  # 0文字の要素をカット
        return sorted(titles, key=lambda x: len(x), reverse=True)[0].strip()  # 最長の要素を返す

    def _get_title(self, url):
        title = ''
        root, ext = os.path.splitext(url)
        if ext in image_extensions:
            time.sleep(3)  # for avoiding to be treated as spam by Google
            results = google_image.search(url, best_kwds_max_length=18)
            keywords = filter(lambda x: not x.isdigit(), results['best_keywords'])
            title = ''.join(keywords)
        elif not ext in ignore_extensions:
            self.logger.info('Retrieve web resource: %s' % url)
            html = web.open_url(url)
            soup = BeautifulSoup(html)
            title = soup.title.string
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

    def run(self, hour_range=HOUR_RANGE, twitter_api=None):
        posts = kuzuha.search('http', _filter=kuzuha.build_date_filter_by_range({'hours': hour_range}))
        urls = self._count_url(posts)

        tweet = ''
        for (url, count) in urls.most_common():
            if twitter_api and url.startswith('https://twitter.com/'):
                tweet_id = self.extract_tweet_id(url)
                if tweet_id:
                    try:
                        self.logger.info('RT: id=%s (%s)' % (tweet_id, url))
                        twitter_api.api.statuses.retweet(id=tweet_id)
                        continue
                    except:
                        pass
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
