# -*- coding: utf-8 -*-
import sys
from __init__ import *


def filtering(_input, output):
    with open(_input) as infd, open(output, 'a+', encoding='utf8') as outfd:
        for line in infd:
            l = line.rstrip().split(',')
            word = l[0]
            pos = l[4:10]
            if is_valid_word(word, ','.join(pos)):
                outfd.write(line)
            else:
                sys.stderr.write('Ignore: %s\n' % word)


if __name__ == '__main__':
    filtering(sys.argv[1], sys.argv[2])
