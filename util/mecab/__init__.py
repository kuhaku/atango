# -*- coding: utf-8 -*-
import os
import re
import jaconv
import MeCab
import sys
sys.path.append('/work/atango')
from lib import misc
from lib.nlp import mecab as atango_mecab


re_katakana = re.compile('^[アァ-ヶンー]+$')
re_symbol = re.compile("[（）＜＞＊「」、。＝〜!！\?？…・\s]")
MECAB_ARGS = ' -F%m\\t%phl,%phr,%c,%H\\n --unk-format=[UNK]\\n --eos-format= -N 100'
PARTS_OF_SPEECH = {
    '固有名詞': ['', 1288, 1288, 0, '名詞', '固有名詞', '一般', '*', '*', '*', '', '', '', '', ''],
    '名詞': ['', 1285, 1285, 0, '名詞', '一般', '*', '*', '*', '*', '', '', '', '', ''],
}
nolmcb = atango_mecab.MeCabWrapper(
    '-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd -Oyomi')


def get_dicdir():
    result = misc.command('mecab-config --dicdir', True)
    return os.path.join(result[1].strip(), 'original')


dicdir = get_dicdir()


def get_yomi(word, yomi=''):
    def to_yomi(word):
        return nolmcb.parse(word).strip()

    word = re_symbol.sub('', word)
    word = jaconv.hira2kata(word)
    if re_katakana.search(word):
        return word
    elif re_katakana.search(yomi):
        return yomi
    yomi = jaconv.hira2kata(to_yomi(word))
    if re_katakana.search(yomi):
        return yomi
    return '*'


def write_word(word, pos, yomi='', label='', dic=''):
    yomi = yomi or get_yomi(word)
    if isinstance(pos, str):
        pos = PARTS_OF_SPEECH[pos].copy()
    pos[0] = pos[10] = word
    pos[11] = pos[12] = yomi
    if label:
        pos.append(label)
    entry = ','.join(map(str, pos))
    dicpath = os.path.join(dicdir, dic or 'manual.csv')
    with open(dicpath, 'a+', encoding='utf8') as fd:
        fd.write(entry + '\n')
    return entry


def is_contained(word, pos=''):
    tagger = MeCab.Tagger(MECAB_ARGS)
    tagger.parse('')  # for avoiding initialization bug
    tagger.parseNBestInit(word)
    for i in range(100):
        result = tagger.next()
        if not result:
            break
        elif len(result.splitlines()) == 1 and pos in result:
            return True
    return False


def is_name(nodes):
    if len(nodes) == 2:
        if ',姓,' in nodes[0].feature and ',名,' in nodes[1].feature:
            return True
        elif ((',姓,' in nodes[0].feature or ',名,' in nodes[0].feature) and
              ',名詞,接尾,人名,' in nodes[1].feature):
            return True
    elif len(nodes) == 3:
        if (',姓,' in nodes[0].feature and ',名,' in nodes[1].feature and
                ',名詞,接尾,人名,' in nodes[2].feature):
            return True
    return False


def is_valid_in_pos_system(nodes):
    if len(nodes) == 2:
        if (nodes[0].feature.startswith('名詞') and
                nodes[1].feature.startswith('名詞,接尾,形容動詞語幹') and
                len(nodes[0].surface + nodes[1].surface) > 2):
            return False
    return True


def check_nodes(word):
    tagger = MeCab.Tagger()
    tagger.parse('')  # for avoiding initialization bug
    n = tagger.parseToNode(word)
    nodes = []
    while n:
        if not n.feature.startswith('BOS/EOS'):
            nodes.append(n)
        n = n.next
    if is_name(nodes):
        return False
    return is_valid_in_pos_system(nodes)


def is_valid_word(word, pos='', debug=True):
    if is_contained(word, pos):
        sys.stderr.write('Reason: contained\n')
        return False
    if word.isnumeric():
        sys.stderr.write('Reason: numeic\n')
        return False
    if check_nodes(word):
        return True
    return False
