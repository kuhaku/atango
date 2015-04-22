# -*- coding: utf-8 -*-
import MeCab
import re
from collections import Counter
from functools import reduce, partial
from lib.multiprocess import Pool


re_number = re.compile('[0-9,]+')
POS = {'content_word': ('名詞', '動詞', '形容詞', '副詞'),
       'noun': ('名詞,一般', '名詞,サ変接続', '名詞,固有名詞', '名詞,数', '名詞,接尾')}
ROOTFORM_IDX = {'IPA': 6}


class MeCabWrapper(MeCab.Tagger):

    def parse_to_node(self, sentence, bos_eos=False):
        node = self.parseToNode(sentence)
        while node:
            if bos_eos or not node.feature.startswith('BOS/EOS'):
                yield node
            node = node.next


def _is_target_pos(feature, target_pos):
    return feature.startswith(target_pos)


def _extract_rootform(feature, dic='IPA'):
    return feature.split(',')[ROOTFORM_IDX[dic]]


def _extract_surface(node, rootform=False):
    if rootform:
        lemma = _extract_rootform(node.feature)
        if lemma != '*':
            return lemma
    return node.surface


def _extract_phrase(nodes, target_pos, rootform=False):
    phrase = []
    phrase_list = []

    for n in nodes:
        if _is_target_pos(n.feature, target_pos):
            phrase.append(_extract_surface(n, rootform))
        else:
            if len(phrase) > 1:
                for i in range(1, len(phrase) - 1):
                    phrase_list.append(''.join(phrase[i:]))
                    phrase_list.append(''.join(phrase[:-i]))
                phrase_list.append(''.join(phrase))
            phrase = []
    if len(phrase) > 1:
        phrase_list.append(''.join(phrase))
    return phrase_list


def extract_word(sentence, target_pos=POS['noun'], rootform=False, phrase=False):
    if isinstance(target_pos, str):
        target_pos = POS.get(target_pos, (target_pos,))
    m = MeCabWrapper()
    nodes = list(m.parse_to_node(sentence))
    words = [_extract_surface(n, rootform) for n in nodes if _is_target_pos(n.feature, target_pos)]
    if phrase:
        words += _extract_phrase(nodes, target_pos, rootform)
    return words


def count_word(sentence, target_pos='noun', rootform=False, phrase=True):
    if isinstance(target_pos, str):
        target_pos = POS.get(target_pos, (target_pos, ))
    return Counter(extract_word(sentence, target_pos, rootform, phrase))


class MeCabMultiProcessing(object):
    pool = None

    def set_pool(self):
        self.pool = Pool(4)

    def count_doc(self, doc, **kwds):
        if not self.pool:
            self.set_pool()
        f = partial(count_word, **kwds)
        return reduce(lambda x, y: x+y, self.pool.imap_unordered(f, doc))
mmp = MeCabMultiProcessing()
count_doc = mmp.count_doc


def wakati(text):
    """
    Param:
        <str> text
    Return:
        <list> tokens
    """
    mecab_wakati = MeCab.Tagger('-Owakati')
    return mecab_wakati.parse(text).strip().split(" ")


def to_yomi(text):
    mecab_yomi = MeCab.Tagger('-Oyomi')
    yomi = mecab_yomi.parse(text)
    if yomi:
        return yomi.rstrip(" \n").split(" ")
    return ['']

def has_demonstrative(text):
    mecab = MeCabWrapper('-d /usr/local/lib/mecab/dic/jumandic')
    for n in mecab.parse_to_node(text):
        if n.feature.startswith('指示詞'):
            return True
    return False
