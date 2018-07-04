# -*- coding: utf-8 -*-
import re
from collections import Counter, namedtuple
import jaconv
from lib import file_io, kuzuha, normalize, misc
from lib.logger import logger
from lib.nlp.mecab import MeCabWrapper
from lib.regex import re_a_tag


mecab = MeCabWrapper()
NG_WORDS = ('http', '投稿日：')
HEADER = '%s〜%s時要約： \n'
MAX_TWEET_LENGTH = 140
DELIMITER = '/\n'
POST_FORMAT = '%s' + DELIMITER
kigou = re.compile('[！\.,、。・…　]')
Node = namedtuple('Node', 'surface feature pos subpos rootform')
ROOTFORM_IDX = 6


class PopularPost(object):

    def __init__(self):
        self.paraphrases = file_io.read('shorten.json', data=True)
        self.car_shorten_map = file_io.read('shorten_char.json', data=True)

    def count_responses(self, posts):

        def is_valid_post(post):
            return all(ng not in post['text'] and not misc.is_mojie(post['text'])
                       for ng in NG_WORDS)

        res_counter = Counter()
        for post in posts:
            if post.get('text') and 'quoted_by' in post and is_valid_post(post):
                res_counter[post['text']] = post['quoted_by']
        return res_counter

    def prepare(self, text):
        text = normalize.shorten_repeat(text, 3)
        text = jaconv.h2z(text)
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
                logger.debug('Skip 係助詞 は,も: %d' % i)
                pass
            elif node.surface == 'ん' and '未然形' in result[-1][1].feature:
                result.append((node.surface, node))
            elif node.surface == 'から' and node.subpos == '接続助詞':
                result.append((node.surface, node))
            elif node.surface in ('けど', 'けれど') and node.subpos == '接続助詞':
                result.append(('が', node))
                logger.debug('Replace %s -> が: %d' % (node.surface, i))
            elif node.subpos == '終助詞' and result:
                if result[-1][1].pos == '助動詞' and result[-1][0] != 'ん':
                    del_node = result.pop(-1)
                    logger.debug('Delete %s: %d' % (del_node[0], i))
                logger.debug('Ignore %s: %d' % (node.surface, i))
            elif node.surface in ('たら', 'た') and '連用タ接続' in result[-1][1].feature:
                if result[-1][1].rootform not in ('*', ''):
                    result[-1] = (result[-1][1].surface, result[-1][1])
                result.append((node.surface, node))
                logger.debug('連用タ接続 %s %s: %d' % (result[-1][0], node.surface, i))
            elif '連用タ接続' in node.feature and node.rootform not in ('よい', '良い'):
                if node.rootform not in ('*', ''):
                    result.append((node.rootform, node))
                    logger.debug('連用タ接続 %s %s: %d' % (node.surface, node.rootform, i))
            elif node.pos == '助動詞' and result and result[-1][0] == 'ん':
                del_node = result.pop(-1)
                logger.debug('Delete %s: %d' % (del_node[0], i))
            elif (node.surface == 'か' and node.pos == '助詞' and
                    (result[-1][0] in ('ん', 'の') and result[-1][1].pos == '名詞')):
                del_node = result.pop(-1)
                logger.debug('Delete %s: %d' % (del_node[0], i))
            elif node.pos == '記号' and result and (result[-1][0] == 'か' and result[-1][1].pos == '助詞'):
                del_node = result.pop(-1)
                result.append((node.surface, node))
                logger.debug('Replace %s -> %s: %d' % (del_node[0], result[-1][0], i))
            elif (result and result[-1][0] != 'ん' and 
                    node.subpos in ('接続助詞', '格助詞', '終助詞', 'フィラー', '副詞化')):
                if result[-1][1].rootform not in ('*', ''):
                    result[-1] = (result[-1][1].rootform, result[-1][1])
                    logger.debug('Replace %s -> %s: %d' % (result[-1][1].surface, result[-1][0], i))
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
            text = text.replace('かるて', 'かって')
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
        dt_filter = kuzuha.build_hour_filter(interval)
        posts = misc.retry(10, interval=0.5, allow_null=False)(kuzuha.search)('',
                                                                              _filter=dt_filter,
                                                                              sort=[])
        post_counter = self.count_responses(posts)
        start = int(dt_filter['range']['dt']['gte'][11:13])
        end = int(dt_filter['range']['dt']['lte'][11:13])
        end = 0 if end == 23 else end + 1
        result = self.make_summary(post_counter, start, end)
        return result

if __name__ == '__main__':
    logger.enable_stream_handler()
    logger.enable_debug()
    pp = PopularPost()
    while True:
        text = input()
        print(pp.summarize(text))
