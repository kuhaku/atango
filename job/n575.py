# -*- coding: utf-8 -*-
import re
from lib import normalize, regex, kuzuha
from lib.nlp import cabocha


re_chokuon = re.compile(r'[ゃゅょャュョ]')

class Senryu(object):

    @staticmethod
    def is_valid575(tokens):
        if tokens[0] in ('に', 'は', 'か', 'が', 'や', 'を', 'で', 'と', 'の', 'も'):
            return False
        if ''.join(tokens)[-1] == 'っ':
            return False
        return True

    @staticmethod
    def is_valid_pos(feature):
        if feature[0] in ('助詞'):
            return False
        return True

    def extract575(self, text):
        phase = 0
        count = 0
        parts = []
        tokens = []
        yomi_count = []
        features = []
        for chunk in cabocha.parse(text):
            for token in chunk['tokens']:
                length = 0
                feature = token.feature.split(',')
                if feature[0] == '記号':
                    length = 0
                elif len(feature) >= 8:
                    length = len(re_chokuon.sub('', feature[7]))
                else:
                    length = len(re_chokuon.sub('', token.surface))
                yomi_count.append(length)
                tokens.append(token.surface)
                features.append(feature)
                if phase == 2 and sum(yomi_count) == 17 and self.is_valid575(tokens):
                    return ''.join(tokens)
                elif phase == 2 and sum(yomi_count) == 13:
                    if not self.is_valid_pos(feature):
                        return None
                elif phase == 1 and sum(yomi_count) == 12:
                    phase = 2
                elif phase == 1 and sum(yomi_count) == 6:
                    if not self.is_valid_pos(feature):
                        return None
                elif phase == 0 and sum(yomi_count) == 5:
                    phase = 1
                elif phase == 0 and sum(yomi_count) > 5 and yomi_count:
                    yomi_count.pop(0)
                    tokens.pop(0)
                    features.pop(0)
                elif phase == 0 and length > 5:
                    phase = 0
                    yomi_count = []
                    tokens = []
                    features = []

    def run(self):
        _filter = kuzuha.build_hour_filter(1)
        for post in kuzuha.search(_filter=_filter, sort=[('_score', 'desc')]):
            text = normalize.normalize(post['text'], repeat=4)
            text = regex.re_html_tag.sub('', text)
            text = regex.re_url.sub('', text)
            result = self.extract575(text)
            if result:
                return result + ' #くわ川柳'
