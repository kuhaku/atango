# -*- coding: utf-8 -*-
from lib import misc, file_io, normalize, google_image, web

RESPONSES = (
    "ああ(;´Д`)",
    "ﾏｼﾞで？(;´Д`)",
    "ﾜﾗﾀ(;´Д`)",
    "何言ってるんだこの人(;´Д`)",
    "ﾔﾊﾞｲな(;´Д`)",
    "畏れ(;´Д`)",
    "わかってるよ(;´Д`)",
    "つーかまんこだろ"
)
config = file_io.read('atango.json')['Reply']


def _random_choice(*arg):
    while True:
        yield misc.choice(RESPONSES)


def respond_by_rule(*arg):
    if any(substr in arg[0] for substr in config['VALENTINE']):
        yield give_valentine_present()
    elif any(substr in arg[0] for substr in config['PRESENT']):
        yield give_present()
    elif any(substr in arg[0] for substr in config['HAIKU']):
        yield haiku()


def present_at_event(*arg):
    while True:
        yield give_valentine_present()


def give_present(*arg):
    present_list = file_io.read('present.txt')
    sentence = misc.choice(present_list)
    while ('集計' in sentence or 'シュウケイ' in sentence or 'を' not in sentence or
            sentence.endswith('萌え') or len(sentence) < 3):
        sentence = misc.choice(present_list)
    present = normalize.remove_emoticon(sentence)
    present = present.replace('！', '').replace('!', '')
    present = present.replace('漏れの', '').replace('俺の', '').replace('俺が', '')
    present = present[:-1] if present.endswith('を') else present
    search_result = google_image.search(present)
    if 'images' in search_result:
        for url in search_result['images']:
            if url.endswith(('.jpg', '.gif', '.png')):
                try:
                    web.download(url, '/tmp/present')
                    break
                except:
                    continue
    sentence = normalize.normalize(sentence)
    return {'text': '%nameに' + sentence, 'media[]': '/tmp/present'}


def give_valentine_present(*arg):
    present_list = file_io.read('valentine.txt')
    present = misc.choice(present_list)
    search_result = google_image.search(present)
    if 'images' in search_result:
        for url in search_result['images']:
            if not url.endswith(('.jpg', '.gif', '.png')):
                continue
            try:
                web.download(url, '/tmp/present')
                break
            except:
                continue
    present = normalize.normalize(present)
    return {'text': '%nameに' + present + 'をヽ(´ー｀)ノ', 'media[]': '/tmp/present'}


def haiku(*arg):
    haiku_list = file_io.read('haiku.txt')
    return misc.choice(haiku_list) + ' #くわ川柳'
