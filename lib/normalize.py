# -*- coding: utf-8 -*-
import re
import html.entities
import itertools
from collections import OrderedDict
import jctconv
import tr
from . import path

# for htmlentity2unicode
re_reference = re.compile("&(#x?[0-9a-f]{,32}|[a-z]{,32});", re.I)
re_hex = re.compile('#x\d{1,32}', re.I)
re_decimal = re.compile('#\d{1,32}', re.I)
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
    text = htmlentity2unicode(text)
    text = text.replace('\r', '\n')
    if emoticon is False:
        text = remove_useless_symbol(text)
        text = text.replace(u'γ⌒ヽ', '')
        text = jctconv.h2z(text)
        text = text.replace(u'よぉ', u'よ').replace(u'よぉ', u'よ')
        text = text.replace(u'よお', u'よ').replace(u'よお', u'よ')
    if repeat:
        text = shorten_repeat(text, repeat)
    return text


def normalize_word(word):
    """
    For identify same word
    """
    word = jctconv.kata2hira(word)
    return word.lower()


def htmlentity2unicode(text):
    u"""
    文字参照を文字に変換
    Based on http://snipplr.com/view/11344/
    """
    included_htmlentities = {}
    if '&' in text and ';' in text:
        for reference in re_reference.findall(text):
            # 実体参照 or 文字参照
            if reference in html.entities.name2codepoint:
                codepoint = html.entities.name2codepoint[reference]
                included_htmlentities["&%s;" % reference] = chr(codepoint)
            # 文字参照(16進)
            elif re_hex.match(reference):
                index = "&%s;" % reference
                included_htmlentities[index] = chr(int(u'0'+reference[1:], 16))
            # 文字参照(10進)
            elif re_decimal.match(reference):
                index = "&%s;" % reference
                included_htmlentities[index] = chr(int(reference[1:]))
    for (reference, char) in included_htmlentities.items():
        text = text.replace(reference, char)
    return text


def remove_emoticon(text):
    text = re_face.sub('', text)
    text = re_left_hand.sub('(', text)
    text = re_right_hand.sub(')', text)
    text = text.replace(u'＾＾', '')
    text = text.replace('^^;', '')
    text = text.replace('^^', '')
    text = re_emoticon.sub('', text)
    text = text.replace('()', '')
    return text


class SynonymUnification(object):

    def __init__(self):
        self.synonym_map = OrderedDict()
        propensity = path.read('propensity.json')
        for (k, v) in sorted(propensity.items(), key=lambda x: len(x[0]), reverse=True):
            self.synonym_map[k] = v

    def unify(self, text):
        for key in self.synonym_map:
            if key in text:
                text = text.replace(key, self.synonym_map[key])
        return text
