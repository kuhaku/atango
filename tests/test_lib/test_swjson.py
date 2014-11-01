# -*- coding: utf-8 -*-
from nose.tools import assert_equals
import os
import time
from lib import swjson, file_io

FILES = ('qwerty.html', 'qwerty_author.html', 'qwerty_post.html', 'usamin.html', 'gikogicom.html')


class testSwJson:

    def __init__(self):
        self.parser = swjson.SwJson()
        self.load_test_data()

    def load_test_data(self):
        wdir = os.path.abspath(os.path.dirname(__file__))
        for filename in FILES:
            attr_name = filename.replace('.', '_')
            path = os.path.join(wdir, filename)
            content = file_io.read_text_file(path)
            setattr(self, attr_name, content)

    def test_identify_site(self):
        got = self.parser._identify_site(self.qwerty_html)
        assert_equals(got, 'KUZUHA')
        got = self.parser._identify_site(self.usamin_html)
        assert_equals(got, 'USAMIN')
        got = self.parser._identify_site(self.gikogicom_html)
        assert_equals(got, 'GIKOGICOM')

    def test_extract_articles(self):
        got_articles = self.parser._extract_articles(self.qwerty_html)
        assert_equals(len(list(got_articles)), 2)
        got_articles = self.parser._extract_articles(self.usamin_html)
        assert_equals(len(list(got_articles)), 3)
        got_articles = self.parser._extract_articles(self.gikogicom_html)
        assert_equals(len(list(got_articles)), 3)

    def test_extract_name(self):
        self.parser.regex = swjson.REGEX['KUZUHA']
        post = self.qwerty_author_html
        got_name = self.parser._extract_name(post, 'author')
        assert_equals(got_name, u'<A href="mailto:admin@qwerty.on.arena.ne.jp">深海</A>')

    def test_extract_post_date(self):
        self.parser.regex = swjson.REGEX['KUZUHA']
        post = self.qwerty_author_html
        got_date = self.parser._extract_post_date(post)
        assert_equals(got_date, '2014-06-08-13-00-48')

    def test_to_unixtime(self):
        epoch = time.localtime(0)
        date = time.strftime('%Y-%m-%d-%H-%M-%S', epoch)
        got = self.parser._to_unixtime(date)
        assert_equals(got, 0.0)

    def test_extract_post_text(self):
        self.parser.regex = swjson.REGEX['KUZUHA']
        article = list(self.parser._extract_articles(self.qwerty_html))[-1]
        got_post_text = self.parser._extract_post_text(article)
        assert_equals(got_post_text, u'ﾏﾐさん！(;´Д`)')

    def test_parse_post_text(self):
        self.parser.regex = swjson.REGEX['KUZUHA']
        html = self.parser._cleansing(self.qwerty_post_html, 'KUZUHA')
        article = list(self.parser._extract_articles(html))[0]
        post_text = self.parser._extract_post_text(article)
        parsed_post_text = self.parser._parse_post_text(post_text)
        assert_equals(parsed_post_text['q2'], [u'(;´Д`)'])
        assert_equals(parsed_post_text['q1'], [u'ヽ(´ー｀)ノ'])
        assert_equals(parsed_post_text['text'],
                      [u'v(*´Д､ﾟ)v',
                       u'<A href="#25721977">参考：2014/06/15(日)00時06分32秒</A>'])

    def test_link_by_quote(self):
        self.parser.regex = swjson.REGEX['KUZUHA']
        html = self.parser._cleansing(self.qwerty_post_html, 'KUZUHA')
        posts = {}
        for article in list(self.parser._extract_articles(html))[::-1]:
            id = self.parser._extract_id(article)
            posts[id] = {}
            post_text = self.parser._extract_post_text(article)
            parsed_post_text = self.parser._parse_post_text(post_text)
            text, posts = self.parser._link_by_quote(parsed_post_text['text'], id, posts)
        assert_equals(posts[u'25721989']['quote'], u'25721977')
        assert_equals(posts[u'25721977']['quoted_by'], [u'25721989'])
        assert_equals(text, [u'v(*´Д､ﾟ)v'])

    def test_parse(self):
        self.parser.regex = swjson.REGEX['KUZUHA']
        html = self.parser._cleansing(self.qwerty_post_html, 'KUZUHA')
        posts = self.parser._parse(html)
        assert_equals(posts[u'25721989']['quote'], u'25721977')
        assert_equals(posts[u'25721977']['quoted_by'], [u'25721989'])
