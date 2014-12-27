# -*- coding: utf-8 -*-
import sys
import re
import time
import tempfile
import os
import gzip
import zipfile
from collections import OrderedDict
import shutil
from bs4 import BeautifulSoup
import jctconv
from lib import web
from lib.nlp import mecab


RSS_URL = (
    'http://www.google.co.jp/trends/hottrends/atom/feed?pn=p4',
    'http://searchranking.yahoo.co.jp/rss/burst_ranking-rss.xml',
    'http://search.biglobe.ne.jp/rss/ranking.xml'
)

SYOBOCAL_BASE_URL = 'http://cal.syoboi.jp'
SYOBOCAL_START_URL = SYOBOCAL_BASE_URL + '/list'
WIKIPEDIA_URL = 'http://dumps.wikimedia.org/jawiki/latest/jawiki-latest-all-titles-in-ns0.gz'
HATENA_URL = 'http://web-apps.nbookmark.com/hatena-dic/hatena_msime_nocomment.zip'

re_sumikakko = re.compile("【[^】]+】")
re_symbol = re.compile("[（）＜＞＊「」、。＝〜!！\?？…・\s\.,\'\"\(\)\-_]")
re_tyouon = re.compile("[−−─━]")
re_date = re.compile('\d{1,2}月\d{1,2}日')
re_katakana_hiragana = re.compile("[ァ-ンぁ-んー]+")


re_title_url = re.compile('<a href="(?P<url>/tid/[0-9]+)">(?P<title>[^<]+)</a>')
#re_title_name = re.compile(r'<meta name="keywords" content="([^,]+),')
re_title_yomi = re.compile(r'<tr><th>よみ</th><td>([^<]+)</td></tr>')
INTERVAL = 0.2

WORD_MAX_LENGTH = 20
POS = ["", "1288", "1288", "0", "名詞", "固有名詞", "一般", "*", "*", "*", "", "", "", "", "", ""]
UNK = '!!!UNK!!!'
COST = '0'


class WebNeologism(object):

    def __init__(self, mecab_dicdir):
        self.output_path = os.path.join(mecab_dicdir, 'web_neologism.csv')
        self.tempdir = tempfile.mkdtemp()
        self.wikipedia_path = os.path.join(self.tempdir, 'wiki.gz')
        self.hatena_kwd_path = os.path.join(self.tempdir, 'hatena.zip')

        self.mecab_unk = mecab.MeCabWrapper('--unk-feature=%s' % UNK)
        self.mecab_name = mecab.MeCabWrapper('-F%f[3]')

    def get_trend_search_query(self, url):
        html = web.open_url(url)
        soup = BeautifulSoup(html)
        for item in soup.find_all('item'):
            title = item.find('title')
            keyword = str(title.string).strip()
            keyword = re_sumikakko.sub('', keyword)
            if ' ' in keyword:
                for kwd in keyword.split(' '):
                    yield kwd
            else:
                yield keyword

    def is_contained_in_mecab_dic(self, word):
        for (i, node) in enumerate(self.mecab_unk.parse_to_node(word)):
            if UNK in node.feature:
                #print(word, node.surface, 'UNK')
                return False
        if i > 1:
            #print(word, i)
            return False
        return True

    def is_name(self, word):
        result = self.mecab_name.parse(word).rstrip().replace('EOS', '')
        return result == '姓名'

    def is_valid_word(self, word):
        if len(word) > WORD_MAX_LENGTH:  # max文字以上の単語は弾く
            return False
        if '(' in word or ',' in word:
            return False
        if word.isdigit() or word.isalpha():
            return False
        if re_date.search(word):
            return False
        if self.is_name(word):
            return False
        if self.is_contained_in_mecab_dic(word):
            return False
        return True

    def get_yomi(self, word):
        def normalize(s):
            s = jctconv.hira2kata(s).replace('・', '')
            s = re_symbol.sub('', s)
            return re_tyouon.sub('ー', s)

        normalized_word = normalize(word)
        if re_katakana_hiragana.match(normalized_word):
            return normalized_word
        yomi = ''.join(mecab.to_yomi(word))
        yomi = normalize(yomi)
        if re_katakana_hiragana.match(yomi):
            return yomi
        return '*'

    def normalize_yomi(self, yomi):
        yomi = jctconv.hira2kata(yomi)
        return yomi.replace('ウ゛', 'ヴ').replace(' ', '')

    def to_mecab_format(self, word, yomi, label):
        pos = POS.copy()
        pos[10] = pos[0] = word
        pos[11] = pos[12] = self.normalize_yomi(yomi)
        pos[-1] = label
        return ','.join(pos)

    def write(self, lines):
        if os.path.exists(self.output_path):
            write_mode = 'a+'
        else:
            write_mode = 'w'
        with open(self.output_path, write_mode, encoding='utf8') as fd:
            fd.write('\n'.join(lines) + '\n')

    def retrieve_from_search_query(self):
        lines = []
        for url in RSS_URL:
            for word in self.get_trend_search_query(url):
                if not self.is_valid_word(word):
                    continue
                yomi = self.get_yomi(word)
                lines.append(self.to_mecab_format(word, yomi, 'SQ'))
            if lines:
                self.write(lines)

    def retrieve_from_syobocal(self):
        start_html = web.open_url(SYOBOCAL_START_URL, params={'cat': 1})
        lines = []
        for (url_part, title_name) in re_title_url.findall(start_html):
            if not self.is_valid_word(title_name):
                continue
            title_url = SYOBOCAL_BASE_URL + url_part
            title_html = web.open_url(title_url)
            title_yomi = ''.join(re_title_yomi.findall(title_html))
            lines.append(self.to_mecab_format(title_name, title_yomi, 'SC'))
            time.sleep(INTERVAL)
        if lines:
            self.write(lines)

    def download(self):
        web.download(WIKIPEDIA_URL, self.wikipedia_path)
        web.download(HATENA_URL, self.hatena_kwd_path)

    def extract_words_from_hatena(self):
        with zipfile.ZipFile(self.hatena_kwd_path) as hatena_fd:
            filename = hatena_fd.namelist()[0]
            hatena_fd.extract(filename, self.tempdir)
        filename = os.path.join(self.tempdir, filename)
        valid_words = {}
        with open(filename, 'r', encoding='utf16') as fd:
            for line in fd:
                columns = line.split('\t')
                if len(columns) < 3:
                    continue
                yomi = columns[0]
                word = columns[1]
                if self.is_valid_word(word):
                    valid_words[word] = yomi
        return valid_words

    def extract_common_words(self, valid_words):
        with gzip.open(self.wikipedia_path, 'r') as wp_fd:
            for line in wp_fd:
                word = line.decode('utf-8').strip()
                if word in valid_words:
                    yield word

    def retrieve_from_wikipedia_hatena(self):
        self.download()
        valid_words = self.extract_words_from_hatena()
        lines = []
        for word in self.extract_common_words(valid_words):
            yomi = valid_words[word]
            lines.append(self.to_mecab_format(word, yomi, 'WH'))
        if lines:
            self.write(lines)

    def delete_duplicate_word(self):
        words = OrderedDict()
        with open(self.output_path, 'r', encoding='utf8') as fd:
            for line in fd:
                surface = line.split(',')[0]
                if surface not in words:
                    words[surface] = line
        with open(self.output_path, 'w', encoding='utf8') as fd:
            fd.write(''.join(words.values()))

    def get(self):
        try:
            self.retrieve_from_search_query()
            self.retrieve_from_syobocal()
            self.retrieve_from_wikipedia_hatena()
            self.delete_duplicate_word()
        finally:
            if os.path.exists(self.tempdir):
                shutil.rmtree(self.tempdir)


if __name__ == '__main__':
    wn = WebNeologism(sys.argv[1])
    wn.get()
