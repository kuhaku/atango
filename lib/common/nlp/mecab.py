# -*- coding: utf-8 -*-
import MeCab
import re
from collections import Counter
from functools import reduce


re_number = re.compile('[0-9,]+')
POS = {'content_word': ('名詞', '動詞', '形容詞', '副詞'),
       'noun': ('名詞,一般', '名詞,サ変接続', '名詞,固有名詞', '名詞,数')}
ROOTFORM_IDX = {'IPA': 6}


class MeCabWrapper(MeCab.Tagger):

    def __init__(self, mecab_args=''):
        self.mecab = MeCab.Tagger(mecab_args)
        self.mecab.parse('')
        super(MeCabWrapper, self).__init__()

    def parse_to_node(self, sentence, bos_eos=False):
        node = self.mecab.parseToNode(sentence)
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
        return _extract_rootform(node.feature)
    return node.surface


def _extract_phrase(nodes, target_pos):
    phrase = []
    phrase_list = []

    for n in nodes:
        if _is_target_pos(n.feature, target_pos):
            phrase.append(n.surface)
        else:
            if len(phrase) > 1:
                phrase_list.append(''.join(phrase))
            phrase = []
    return phrase_list


def extract_word(sentence, target_pos=(), rootform=False, phrase=False):
    m = MeCabWrapper()
    nodes = [node for node in m.parse_to_node(sentence)]
    words = [_extract_surface(n, rootform) for n in nodes
             if _is_target_pos(n.feature, target_pos)]
    if phrase:
        words += _extract_phrase(nodes, target_pos)
    return words


def count_word(sentence, target_pos='noun', rootform=False, phrase=True):
    counter = Counter()
    if isinstance(target_pos, str):
        target_pos = POS.get(target_pos, tuple())
    for word in extract_word(sentence, target_pos, rootform, phrase):
        counter[word] += 1
    return counter


def count_doc(doc):
    return reduce(lambda x, y: x+y, map(count_word, doc))


def wakati(text):
    """
    Param:
        <str> text
    Return:
        <list> tokens
    """
    mecab_wakati = MeCab.Tagger('-Owakati')
    return mecab_wakati.parse(text).strip().split(" ")
