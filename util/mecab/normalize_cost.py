# -*- coding: utf-8 -*-
import sys
from collections import defaultdict
import operator
from functools import reduce
import numpy as np

sys.path.append('/work/atango')
from lib.misc import map_dict


def get_costs_each_pos(ipadic_file):
    pos_costs = defaultdict(list)
    with open(ipadic_file, 'r', encoding='utf8') as fd:
        for line in fd:
            columns = line.rstrip().split(',')
            if len(columns[0]) == 1:
                pos = ','.join(columns[4:10])
                pos_costs[pos].append(int(columns[3]))
    return pos_costs


def compute_means(pos_costs):
    return map_dict(np.mean, pos_costs)


def compute_total_means(pos_means):
    means = reduce(operator.add, pos_means.values())
    return str(int(np.mean(means)))


def str_ceil_means(pos_means):
    to_ceil_str = lambda x: str(int(x))
    return map_dict(to_ceil_str, pos_means)


def replace_costs(target_file, pos_means, total_mean):
    result = []
    with open(target_file, 'r', encoding='utf8') as fd:
        for line in fd:
            columns = line.rstrip().split(',')
            pos = ','.join(columns[4:10])
            columns[3] = pos_means.get(pos, total_mean)
            result.append(','.join(columns))
    return result


def write_result(target_file, result):
    filename = target_file.replace('.temp', '.csv')
    with open(filename, 'w', encoding='utf8') as fd:
        fd.write('\n'.join(result))


if __name__ == '__main__':
    ipadic_file = sys.argv[1]
    target_file = sys.argv[2]

    pos_costs = get_costs_each_pos(ipadic_file)
    pos_means = compute_means(pos_costs)
    total_mean = compute_total_means(pos_means)
    pos_means = str_ceil_means(pos_means)

    result = replace_costs(target_file, pos_means, total_mean)
    write_result(target_file, result)
