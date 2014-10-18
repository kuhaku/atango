# -*- coding: utf-8 -*-
from nose.tools import assert_true, assert_equals
import time
from collections import Counter
from bs4 import BeautifulSoup
from lib import google_image


# Mami-san Image
IMAGE_URL = ('http://aniapp.animate.tv/wp-content/themes/atv/images/special/'
             'madokamagica-tps-mami/chara_01.jpg')


class test_GoogleSearchByImageUtils(object):

    def __init__(self):
        self.sbiutil = google_image.GoogleSearchByImageUtils()

    def wait(self):
        time.sleep(0.2)  # wait for avoiding to be treated as spam by Google

    def test_search(self):
        self.wait()
        actual = self.sbiutil.search(IMAGE_URL)
        assert_true('マミ' in actual)

    def test_extract_best_guess_tag(self):
        self.wait()
        result_html = self.sbiutil.search(IMAGE_URL)
        actual = self.sbiutil.extract_best_guess_tag(result_html)
        assert_true('マミ' in actual)

    def test_has_captcha(self):
        pass

    def test_extract_titles(self):
        self.wait()
        result_html = self.sbiutil.search(IMAGE_URL)
        soup = BeautifulSoup(result_html)
        actual = self.sbiutil.extract_titles(soup)
        assert_true(any('マミ' in snippet for snippet in actual))

    def test_extract_snippets(self):
        self.wait()
        result_html = self.sbiutil.search(IMAGE_URL)
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
