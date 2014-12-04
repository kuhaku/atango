# -*- coding: utf-8 -*-
import re
from collections import Counter
from bs4 import BeautifulSoup
from . import web, path
from .nlp import mecab


GOOGLE_BASE_URL = 'http://www.google.co.jp/'
GOOGLE_SEARCH_BY_ENDPOINT = 'http://images.google.co.jp/searchbyimage?hl=ja&image_url='

re_best_guess = re.compile(u'この画像の最良の推測結果:.*?>(.*?)</a>',
                           re.IGNORECASE | re.MULTILINE)
re_html_tag = re.compile('<[^>]+>')

my_mecab = mecab.MeCabWrapper()
ng_tags = path.read('ng_tags.json')


class GoogleSearchByImageUtils(object):

    @staticmethod
    def search(image_url):
        result_url = GOOGLE_SEARCH_BY_ENDPOINT + image_url
        referer = 'http://www.google.co.jp/imghp'
        return web.open_url(result_url, referer=referer)

    @staticmethod
    def extract_best_guess_tag(html):
        match = re_best_guess.search(html)
        if match:
            best_guess = match.group(1)
            best_guess = best_guess.title()
            best_guess = best_guess.replace(' ', '')
            return mecab.wakati(best_guess)
        return []

    @staticmethod
    def has_captcha(soup):
        captcha = soup.find_all('input', {'name': 'captcha'})
        if captcha:
            raise Exception('Oh! Shit! Fuck CAPTCHA!')
        return False

    @staticmethod
    def extract_titles(soup):
        titles = []
        for anchor in soup.select('h3 a'):
            anchor = re_html_tag.sub('', str(anchor))
            if (len(anchor) > 30 and 'Visually similar images' not in anchor and
               '類似の画像' not in anchor):
                titles.append(anchor)
        return titles

    @staticmethod
    def extract_snippets(soup):
        snippets = []
        for snippet in soup.select('div li div div div span'):
            snippet = re_html_tag.sub('', str(snippet))
            if len(snippet) > 30:
                snippets.append(snippet)
        return snippets

    @staticmethod
    def extract_keywords(texts):
        keywords = Counter()
        for text in texts:
            keywords += mecab.count_word(text)
        return keywords

    @staticmethod
    def slim_keywords(keywords):
        result = []
        for kwd in keywords:
            for (i, contained_kwd) in enumerate(result):
                if contained_kwd in kwd:
                    result[i] = kwd
            result.append(kwd)
        return list(sorted(set(result), key=result.index))

    def most_common_keywords(self, best_guess, keywords, max_length=50):
        if best_guess:
            most_common_kwds = best_guess
            length = sum([len(kwd) for kwd in best_guess])
        else:
            most_common_kwds= []
            length = 0
        for (keyword, count) in keywords.most_common():
            if not (keyword in ng_tags or any(keyword in kwds for kwds in most_common_kwds)):
                length += len(keyword)
                if length <= max_length:
                    most_common_kwds.append(keyword)
        return self.slim_keywords(most_common_kwds)


def search(image_url, best_kwds_max_length=50):
    sbiutil = GoogleSearchByImageUtils()
    result = {}

    result['result_page'] = sbiutil.search(image_url)
    result['best_guess'] = sbiutil.extract_best_guess_tag(result['result_page'])
    soup_result_page = BeautifulSoup(result['result_page'])
    if not sbiutil.has_captcha(soup_result_page):
        result['titles'] = sbiutil.extract_titles(soup_result_page)
        result['snippets'] = sbiutil.extract_snippets(soup_result_page)
        result['keywords'] = sbiutil.extract_keywords(result['snippets'])
        result['best_keywords'] = sbiutil.most_common_keywords(result['best_guess'],
                                                               result['keywords'],
                                                               best_kwds_max_length)
    return result
