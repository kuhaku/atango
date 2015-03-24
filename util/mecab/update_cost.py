# -*- coding: utf-8 -*-
import re
import sys
import MeCab
import numpy as np

re_hiragana = re.compile('^[ぁ-ゖ]+$')


def get_cost(word, mecab, line):
    parse_result = mecab.parse(word).rstrip()[:-4]
    columns = parse_result.split(',')
    former_connection_cost = int(columns[0])
    total_cost = int(columns[-1])
    cost = total_cost - former_connection_cost
    coefficient = 0.25
    if '記号,一般' in line:
        coefficient = 0.95
    elif '名詞,固有名詞,人名,姓' in line:
        coefficient = 0.1
    elif ('名詞,一般' in line or '名詞,固有名詞,一般' in line) and re_hiragana.match(word):
        coefficient = 0.9
    return str(int(cost - np.abs(cost * coefficient)))


if __name__ == '__main__':
    input_file = sys.argv[1]
    dicpath = sys.argv[2]
    mecab = MeCab.Tagger('-F%pC,%pc| -d ' + dicpath)
    result = []
    with open(input_file, 'r', encoding='utf8') as input_fd:
        for line in input_fd:
            columns = line.rstrip().split(',')
            columns[3] = get_cost(columns[0], mecab, line)
            result.append(','.join(columns))
    output_file = input_file.replace('.temp', '.csv')
    with open(output_file, 'w', encoding='utf8') as output_fd:
        output_fd.write('\n'.join(result))
