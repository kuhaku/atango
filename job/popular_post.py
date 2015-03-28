# -*- coding: utf-8 -*-
import re
from collections import Counter, namedtuple
import jctconv
from lib import file_io, kuzuha, normalize, misc
from lib.logger import logger
from lib.nlp.mecab import MeCabWrapper
from lib.regex import re_a_tag


mecab = MeCabWrapper()
NG_WORDS = ('http', '投稿日：')
HEADER = '%s〜%s時要約： \n'
MAX_TWEET_LENGTH = 140
DELIMITER = '/ \n'
POST_FORMAT = '%s' + DELIMITER
kigou = re.compile('[！\.,、。・…　]')
Node = namedtuple('Node', 'surface feature pos subpos rootform')
ROOTFORM_IDX = 6


class PopularPost(object):

    def __init__(self):
        self.paraphrases = file_io.read('shorten.json')
        self.car_shorten_map = file_io.read('shorten_char.json')

    def count_responses(self, posts):

        def is_valid_post(post):
            return all(ng not in post['text'] and not misc.is_mojie(post['text'])
                       for ng in NG_WORDS)

        res_counter = Counter()
        for post in posts.values():
            if post.get('text') and 'quoted_by' in post and is_valid_post(post):
                res_counter[post['text']] = post['quoted_by']
        return res_counter

    def prepare(self, text):
        text = normalize.shorten_repeat(text, 3)
        text = jctconv.h2z(text)
        text = re_a_tag.sub('', text)
        text = kigou.sub('', text)
        for (old, new) in self.paraphrases['before'].items():
            text = text.replace(old, new)
        return text

    def to_nodes(self, sentence):
        result = []
        for node in mecab.parse_to_node(sentence):
            surface = node.surface
            feature = node.feature.split(',')
            pos = feature[0]
            subpos = feature[1]
            rootform = feature[ROOTFORM_IDX]
            result.append(Node(surface, feature, pos, subpos, rootform))
        return result

    def _to_natural_sentence(self, nodes):
        result = [(nodes[0].surface, nodes[0])]
        for (i, node) in enumerate(nodes[1:]):
            if node.subpos == '係助詞' and node.rootform in ('は', 'も'):
                pass
            elif node.surface == 'から' and node.subpos == '接続助詞':
                result.append((node.surface, node))
            elif node.surface in ('けど', 'けれど') and node.subpos == '接続助詞':
                result.append(('が', node))
            elif node.subpos == '終助詞' and result[-1][1].pos == '助動詞':
                result.pop(-1)
            elif node.surface == 'たら' and '連用タ接続' in result[-1][1].feature:
                if result[-1][1].rootform not in ('*', ''):
                    result[-1] = (result[-1][1].surface, result[-1])
                result.append((node.surface, node))
            elif '連用タ接続' in node.feature and node.rootform not in ('よい', '良い'):
                if node.rootform not in ('*', ''):
                    result.append((node.rootform, node))
            elif node.pos == '助動詞' and result[-1][0] == 'ん':
                result.pop(-1)
            elif (node.surface == 'か' and node.pos == '助詞' and
                    (result[-1][0] in ('ん', 'の') and result[-1][1].pos == '名詞')):
                result.pop(-1)
            elif node.pos == '記号' and (result[-1][0] == 'か' and result[-1][1].pos == '助詞'):
                result.pop(-1)
                result.append((node.surface, node))
            elif node.subpos in ('接続助詞', '格助詞', '終助詞', 'フィラー'):
                if result[-1][1].rootform not in ('*', ''):
                    result[-1] = (result[-1][1].rootform, result[-1])
            elif node.pos in ('接続詞'):
                pass
            elif node.pos == '助詞' and node.subpos == '連体化':
                pass
            elif node.pos == '助動詞' and node.rootform == 'です':
                pass
            elif node.pos == '名詞':
                if len(node.rootform) < len(node.surface) and node.rootform not in ('*', ''):
                    result.append((node.rootform, node))
                else:
                    result.append((node.surface, node))
            else:
                result.append((node.surface, node))
        return ''.join([n[0] for n in result])

    def simplify_sentence(self, sentence):
        nodes = self.to_nodes(sentence)
        for n in nodes:
            logger.debug('%s,%s' % (n.surface, ','.join(n.feature)))
        if nodes:
            return self._to_natural_sentence(nodes)

    def summarize(self, text):
        text = self.prepare(text)
        logger.debug(text)
        text = self.simplify_sentence(text)
        if text:
            text = text.replace('"', '')
            if text.endswith('んじゃ'):
                text = text.replace('んじゃ', '')
            for (old, new) in sorted(self.paraphrases['after'].items(), key=lambda x: len(x[0]),
                                     reverse=True):
                text = text.replace(old, new)
            for (old, new) in sorted(self.car_shorten_map.items(), key=lambda x: len(x[0]),
                                     reverse=True):
                text = text.replace(old, new)
            if text and text[-1] in ('な', 'だ'):
                text = text[:-1]
            text = text.replace('るてる', 'ってる')
            text = text.replace('書くた', '書いた')
            logger.debug(text)
            return text

    def make_summary(self, post_counter, s1, s2):
        header = '%s〜%s時要約： \n'
        result = header % (s1, s2)
        for (post, count) in post_counter.most_common():
            post = self.summarize(post)
            if len(result) < MAX_TWEET_LENGTH:
                if post:
                    if len(post) > 25:
                        post = post[:25] + '…'
                    if len(post) + len(result) < MAX_TWEET_LENGTH:
                        result += POST_FORMAT % (post)
            else:
                break
        return result[:-3]

    def run(self, interval=1):
        params = kuzuha.gen_params('', {'hour': interval})
        posts = kuzuha.get_log_as_dict('qwerty', params, url=True)
        post_counter = self.count_responses(posts)
        result = self.make_summary(post_counter, params['s1'], params['s2'])
        return result

if __name__ == '__main__':
    pp = PopularPost()
    while True:
        text = input()
        print(pp.summarize(text))
