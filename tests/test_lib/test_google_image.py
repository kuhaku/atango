# -*- coding: utf-8 -*-
from nose.tools import assert_true, assert_equals, assert_raises, assert_false
import os
from collections import Counter
from unittest import mock
from bs4 import BeautifulSoup
from lib import google_image


# Mami-san Image
IMAGE_URL = ('http://aniapp.animate.tv/wp-content/themes/atv/images/special/'
             'madokamagica-tps-mami/chara_01.jpg')



def get_search_result(filename):
    wdir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(wdir, filename)
    with open(path, 'r') as fd:
        return fd.read()


class test_GoogleImageSearch(object):

    def __init__(self):
        self.sbiutil = google_image.GoogleImageSearch()

    def test_search_by_url(self):
        actual = self.sbiutil.search_by_url(IMAGE_URL)
        assert_true('マミ' in actual)

    def test_search_by_word(self):
        actual = self.sbiutil.search_by_word('github')
        assert_true('github.com' in actual)

    def test_extract_best_guess_tag(self):
        result_html = get_search_result('search_by_image.html')
        actual = self.sbiutil.extract_best_guess_tag(result_html)
        assert_true(any('マミ' in tag for tag in actual))

    def test_has_captcha(self):
        html = '<input name="captcha"> </input>'
        assert_raises(Exception, self.sbiutil.has_captcha, html)

        soup = BeautifulSoup(get_search_result('search_by_image.html'))
        assert_false(self.sbiutil.has_captcha(soup))

    def test_extract_titles(self):
        result_html = get_search_result('search_by_image.html')
        soup = BeautifulSoup(result_html)
        actual = self.sbiutil.extract_titles(soup)
        assert_true(any('マミ' in snippet for snippet in actual))

    def test_extract_snippets(self):
        result_html = get_search_result('search_by_image.html')
        soup = BeautifulSoup(result_html)
        actual = self.sbiutil.extract_snippets(soup)
        assert_true(any('マミ' in snippet for snippet in actual))

    def test_extract_keywords(self):
        texts = ['おっぱい', 'おっぱい', 'おっぱい']
        actual = self.sbiutil.extract_keywords(texts)
        assert_equals(dict(actual), {'おっぱい': 3})

    def test_slim_keywords(self):
        keywords = ['マミ', 'おっぱい', 'マミパイ']
        actual = self.sbiutil.slim_keywords(keywords)
        assert_equals(actual, ['マミパイ', 'おっぱい'])

    def test_most_common_keywords(self):
        best_guess = ['マミさん']
        kwds = Counter({'おっぱい': 3, 'マミパイ': 2, '乳': 1})
        actual = self.sbiutil.most_common_keywords(best_guess, kwds, max_length=12)
        assert_equals(actual, ['マミさん', 'おっぱい', 'マミパイ'])

    def test_extract_all_image_urls(self):
        html = get_search_result('google_image_github.html')
        soup_result_page = BeautifulSoup(html)
        actual = self.sbiutil.extract_all_image_urls(soup_result_page)
        assert_true(any('github.com' in url for url in actual))


def test_search():
    with mock.patch('lib.google_image.GoogleImageSearch.search_by_url') as m:
        m.return_value = get_search_result('search_by_image.html')
        actual = google_image.search('http://mamigazou')
        assert_true('巴マミ' in actual['best_guess'])
        assert_true('巴マミ' in actual['best_keywords'])
