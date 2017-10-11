# -*- coding: utf-8 -*-
import re
from html.parser import HTMLParser
import itertools
from collections import OrderedDict
import jctconv
import tr
from . import file_io


# for remove_emoticon
re_emoticon = re.compile('\(.*\)')
re_left_hand = re.compile(r'[vヽъ／＼]\(')
re_right_hand = re.compile(r'\)[v／＼ノ]')
re_face = re.compile('[´ﾟ][Дー][`｀ﾟ]')


def shorten_repeat(text, repeat_threshould=2):
    text_length = len(text)
    for (i, repeat_length) in itertools.product(range(text_length), range(1, int(text_length/2))):
        substr = text[i:i+repeat_length]
        right_start = i + repeat_length
        right_end = right_start + repeat_length
        right_substr = text[right_start:right_end]
        num_repeat_substrs = 1
        while substr == right_substr and right_end <= text_length:
            num_repeat_substrs += 1
            right_start += repeat_length
            right_end += repeat_length
            right_substr = text[right_start:right_end]
        if num_repeat_substrs > repeat_threshould:
            text = text.replace(substr*num_repeat_substrs, substr*repeat_threshould)
    return text


USELESS_SYMBOL_CHARS = u'│├┐─┌┘└┬┤┴┼━┃┏┓┛┗┣┳┫┻╋∥　―＼彡＜＞'


def remove_useless_symbol(text):
    return tr.tr(USELESS_SYMBOL_CHARS, '', text, 'd')


def normalize(text, emoticon=False, repeat=None):
    text = HTMLParser().unescape(text)
    text = text.replace('\r', '\n')
    if emoticon is False:
        text = remove_emoticon(text)
        text = jctconv.h2z(text)
        text = text.replace('よぉ', 'よ').replace('よぉ', 'よ')
        text = text.replace('よお', 'よ').replace('よお', 'よ')
    if repeat:
        text = shorten_repeat(text, repeat)
    return text


def normalize_word(word):
    """
    For identify same word
    """
    word = jctconv.kata2hira(word)
    return word.lower()


def remove_emoticon(text):
    text = remove_useless_symbol(text)
    text = text.replace('γ⌒ヽ', '')
    text = re_face.sub('', text)
    text = re_left_hand.sub('(', text)
    text = re_right_hand.sub(')', text)
    text = text.replace('＾＾', '')
    text = text.replace('^^;', '')
    text = text.replace('^^', '')
    text = re_emoticon.sub('', text)
    text = text.replace('()', '')
    return text


class SynonymUnification(object):

    def __init__(self):
        self.synonym_map = OrderedDict()
        propensity = file_io.read('propensity.json', data=True)
        for (k, v) in sorted(propensity.items(), key=lambda x: len(x[0]), reverse=True):
            self.synonym_map[k] = v

    def unify(self, text):
        for key in self.synonym_map:
            if key in text:
                text = text.replace(key, self.synonym_map[key])
        return text
