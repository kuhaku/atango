# -*- coding: utf-8 -*-
import random

from bs4 import BeautifulSoup

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
PYTHON_EXE_PATH = '/work/venv/py36/bin/python'
STYLE_TRANSFER_PATH = '/work/atango/third_party/fast-style-transfer/'
SAFEBOORU_URL = 'https://safebooru.org/index.php?page=dapi&s=post&q=index&tags=chocolate&pid=%s'


def _random_choice(*arg):
    while True:
        yield misc.choice(RESPONSES)


def respond_by_rule(text, *arg):
    if any(substr in text for substr in config['VALENTINE']):
        yield give_valentine_present(text, *arg)
    elif any(substr in text for substr in config['PRESENT']):
        yield give_present()
    elif any(substr in text for substr in config['HAIKU']):
        yield haiku()


def present_at_event(*arg):
    while True:
        yield give_present()


def give_present(*arg):
    present_list = file_io.read('present.txt', data=True)
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
    if random.randint(0, 11) > 8:
        icon_url = arg[1]['icon'].replace('_normal', '')
        filename = icon_url.split('/')[-1]
        web.download(icon_url, '/tmp/%s' % (filename))
        misc.command('%s evaluate.py --checkpoint ../../data/ckpt ' % (PYTHON_EXE_PATH) +
                     '--in-path /tmp/%s --out-path /tmp/%s' % (filename, filename),
                     shell=True, allow_err=True, cwd=STYLE_TRANSFER_PATH)
        return {'text': '%nameをチョコにしてやろうか！(ﾟДﾟ)', 'media[]': '/tmp/%s' % (filename)}
    pid = random.randint(0, 59)
    xml = web.open_url(SAFEBOORU_URL % pid)
    soup = BeautifulSoup(xml, 'lxml')
    post = misc.choice(soup.find_all('post'))
    image_url = 'https:' + post['file_url']
    web.download(image_url, '/tmp/present')
    suffix = '！' * random.randint(0, 59)
    return {'text': '%nameにチョコをヽ(´ー｀)ノ' + suffix, 'media[]': '/tmp/present'}


def haiku(*arg):
    haiku_list = file_io.read('haiku.txt', data=True)
    return misc.choice(haiku_list) + ' #くわ川柳'
