#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import MeCab
import jctconv

DEFALUT_FORMAT = ' -F%m\\t%phl,%phr,%c,%H,%pC,%pn,%pc\\n --eos-format=BOS\\t%pC,%pn,%pc\\n'
MECAB_ARGS_KEYS = 'rdulDOapmMFUBESxbPCtco'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for key in MECAB_ARGS_KEYS:
        parser.add_argument('-%s' % key)
    parser.add_argument('-N', type=int)
    args = parser.parse_args()
    mecab_arg = ''
    for key in MECAB_ARGS_KEYS:
        arg = getattr(args, key)
        if arg:
            mecab_arg += ' -%s%s' % (key, arg)
    if not args.F:
        mecab_arg += DEFALUT_FORMAT
    mecab = MeCab.Tagger(mecab_arg)
    while True:
        sentence = input()
        sentence = jctconv.h2z(sentence)
        if args.N:
            mecab.parseNBestInit(sentence)
            for i in range(args.N):
                result = mecab.next()
                if result:
                    print(result)
                else:
                    break
        else:
            result = mecab.parse(sentence)
            print(result)
