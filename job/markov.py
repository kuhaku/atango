# -*- coding: utf-8 -*-
from lib import app, kuzuha, normalize, regex
from lib.nlp import mecab, markov

BOS = '\x00'
EOS = '\x01'


class MarkovTweet(app.App):

    def run(self, interval=60, min_length=40):
        m_generator = markov.MarkovGenerater()
        m = mecab.MeCabWrapper()
        posts = kuzuha.search('', _filter=kuzuha.build_date_filter_by_range({'minutes': interval}))

        words = []
        for post in posts:
            text = regex.re_a_tag.sub('', post['text'])
            text = normalize.normalize(text)
            if 'アニメ時報' in text:
                continue
            words.append([])
            for line in text.splitlines():
                words[-1].append(BOS)
                for n in m.parse_to_node(line):
                    words[-1].append('%s,%s' % (n.surface, ''.join(n.feature.split(',')[:5])))
                words[-1].append(EOS)
        return m_generator.generate(words, min_length)
