# -*- coding: utf-8 -*-
from glob import glob
import sys
import os
from collections import defaultdict


THRESHOLD = 1000


if __name__ == '__main__':
    base_dic_dir = sys.argv[1]
    store_dir = sys.argv[2]
    pattern = os.path.join(base_dic_dir, sys.argv[3])
    output_bufs = defaultdict(list)
    output_files = {}
    for filename in glob(pattern):
        if filename.endswith('ipadic.csv'):
            continue
        with open(filename, 'r', encoding='utf8') as input_fd:
            for line in input_fd:
                columns = line.rstrip().split(',')
                surface = columns[0]
                length = len(surface)
                if length not in output_files:
                    store_filename = os.path.join(store_dir, '%d.temp' % (length))
                    output_files[length] = open(store_filename, 'w', encoding='utf8')
                if len(output_bufs[length]) > THRESHOLD:
                    output_files[length].write(''.join(output_bufs[length]))
                    output_bufs[length] = []
                else:
                    output_bufs[length].append(line)
    for (length, lines) in output_bufs.items():
        output_files[length].write(''.join(lines))
        output_files[length].close()
