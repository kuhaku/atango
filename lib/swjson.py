# -*- coding: utf-8 -*-
import re
import json
import time
from collections import defaultdict
"""
strange world JSON parser

JSON parser for structuring strange world HTML

[ 投稿番号(21076794) :
    {
    date : 日付(2012-02-10-20-22-14)
    text : 投稿本文(俺は小星ちゃんがいい(;´Д`))
    q1 : 引用符1のテキスト(くぎゅうと結婚したい(;´Д`)家帰ってきたらくぎゅうがお帰りって・・・)
    q2 : 引用符2のテキスト(釘宮理恵好きだけど裸見たいとか思わん(;´Д`)ﾀﾀﾞなら見たいかも)
    quote : 引用した投稿の番号(21076783)
    quoted_by : この投稿を引用した投稿の番号([u'21076796'])
    }
]
"""


REGEX = {
    'KUZUHA': {
        'pre': re.compile(r'(?<=<PRE>).*?(?=</PRE>)', re.S),
        'id': re.compile(r'(?<=<!-- )\d+(?= -->)'),
        'date': re.compile('<FONT[^>]+>投稿日：(?P<Y>\d{4})/(?P<m>\d\d)/(?P<D>\d\d)'
                           '\(.\)(?P<H>\d\d)時(?P<M>\d\d)分(?P<S>\d\d)秒', re.I),
        'quote': re.compile(u'<A href="#(\d+)">参考：', re.I),
        'author': re.compile(u'投稿者：<b>(.+?)</b>', re.I),
        'to': re.compile(u'<FONT size="\+1" color="#fffffe"><B>＞(.+?)</B>', re.I)
    },
    'USAMIN': {
        'pre': re.compile(r'(?<=\><pre>).+?(?=<\/pre>)', re.S),
        'id': re.compile(r'(?<=")\d+(?=")'),
        'date': re.compile(u'<font size="\-1">(?P<Y>\d{4})/(?P<m>\d\d)/(?P<D>\d\d) \(.\) '
                           u'(?P<H>\d\d):(?P<M>\d\d):(?P<S>\d\d)'),
        'quote': re.compile(u'<A href="#(\d+)">参考：.+秒</A>'),
        'author': re.compile(u'投稿者：<b>(.+?)</b>', re.I),
        'to': re.compile(u'<FONT size="\+1" color="#ffffff"><B>＞(.+?)</B>'),
        'resnum': re.compile('\[(\d+)\]'),
        'thread': re.compile('s=([\d]+)">◆')
    },
    'GIKOGICOM': {
        'pre': re.compile(r'(?<=<pre class="msg">)(.+)(?=\n<\/pre>)'),
        'id': re.compile(r'(?<=<div class="m" id="m)\d+(?=">)'),
        'date': re.compile(u'<span class="md">投稿日：(?P<Y>\d{4})/(?P<m>\d\d)/(?P<D>\d\d)'
                           u'\(.\)(?P<H>\d\d)時(?P<M>\d\d)分(?P<S>\d\d)秒'),
        'quote': re.compile('<a href="http://gikogi.com/bbslog/qwerty/id/(\d+)"'),
        'author': re.compile('<span class="mn">([^　\n]+)'),
        'to': re.compile(u'<span class="mt">＞([^　\n]+)')
    }
}

re_hr = re.compile('<hr/?>', re.I)
re_q2 = re.compile('\A(&gt;|>) (&gt;|>) ')
re_q1 = re.compile('\A(&gt;|>) ')
re_link = re.compile('<a[^<]+</a>', re.I)
re_quote_link = re.compile('<a[^>]+>参考：[^秒]+秒</a>', re.I)

class SwJson:

    def __init__(self, **args):
        self.fast = args.get('fast', False)
        self.url = args.get('url', False)
        self.usamin_detail = args.get('usamin_detail', False)

    @staticmethod
    def _identify_site(html):
        """
        Param:
            <str> html
        Return:
            <str> site_name
        """
        if u'<title>Q全文:' in html or u'<title>qwerty全文検索</title>' in html:
            return 'USAMIN'
        elif '(gikogi.com)</title>' in html:
            return 'GIKOGICOM'
        return 'KUZUHA'

    def _cleansing(self, html, site):
        """
        remove unused information
        Params:
            <str> html
            <str> site
        Return:
            <str> html
        """
        html = html.replace(' target="link"', '')
        if site == 'GIKOGICOM':
            html = html[:html.rindex('<hr>')]
            html = html.replace('<span class="q">', '').replace('</span>', '')
        elif site == 'KUZUHA':
            html = html.replace('<FONT color="#ffffff">', '')
            html = html.replace('</FONT>', '')
        return html

    @staticmethod
    def _extract_articles(html):
        """
        Param:
            <str> html
        Return:
            <list <str>> articles
        """
        has_pre = lambda x: '</PRE>' in x or '</pre>' in x
        return filter(has_pre, re_hr.split(html)[1:-1])

    def _extract_id(self, post):
        id_match = self.regex['id'].search(post)
        if id_match:
            return int(id_match.group(0))

    def _extract_name(self, post, person):
        name = self.regex[person].findall(post)
        if name and name[0] != u'　':
            return name[0]

    def _extract_post_date(self, post):
        """
        Param:
            <str> post
        Return:
            <str> date
        """
        return '-'.join(self.regex['date'].findall(post)[0])

    @staticmethod
    def _to_unixtime(date):
        """
        Param:
            <str> date
        Return:
            <str> unixtime
        """
        return int(time.mktime(time.strptime(date, '%Y-%m-%d-%H-%M-%S')))

    def _extract_post_text(self, post):
        return self.regex['pre'].search(post).group(0).rstrip()

    def _parse_post_text(self, pre):
        parsed_post_text = defaultdict(list)
        for line in pre.splitlines():
            if re_q2.search(line):
                parsed_post_text['q2'].append(re_q2.sub('', line))
            elif re_q1.search(line):
                parsed_post_text['q1'].append(line[line.index(' ')+1:])
            elif line:
                parsed_post_text['text'].append(line)
        return parsed_post_text

    def _link_by_quote(self, text, _id, posts):
        quote_match = self.regex['quote'].search(text[-1])
        if quote_match:
            quoted_post_id = int(quote_match.group(1))
            posts[_id]['quote'] = quoted_post_id
            if quoted_post_id not in posts:
                posts[quoted_post_id] = {}
            if 'quoted_by' in posts[quoted_post_id]:
                posts[quoted_post_id]['quoted_by'].append(_id)
            else:
                posts[quoted_post_id]['quoted_by'] = [_id]
            text.pop(-1)
        return (text, posts)

    @staticmethod
    def _delete_anchor_tag(post):
        for item in ('text', 'q1', 'q2', 'author'):
            if item in post:
                if isinstance(post[item], list):
                    post[item] = '\n'.join(post[item])
                post[item] = re_link.sub('', post[item])
        return post

    @staticmethod
    def _delete_quote_link(text):
        text = re_quote_link.sub('', text)
        return text.rstrip()

    def _extract_items(self, post):
        _id = self._extract_id(post)
        if not _id:
            return None
        post_items = {'id': _id}

        pre = self.regex['pre'].findall(post)[0]
        parsed_post_text = self._parse_post_text(pre)

        extraction_target = {'q1': parsed_post_text.get('q1', None),
                             'q2': parsed_post_text.get('q2', None),
                             'text': parsed_post_text.get('text', None),
                             'author': self._extract_name(post, 'author'),
                             'to': self._extract_name(post, 'to'),
                             'date': self._extract_post_date(post),
                             }
        if self.usamin_detail:
            for resnum in self.regex['resnum'].findall(post):
                resnum = int(resnum)
                if resnum > 0:
                    extraction_target['resnum'] = resnum
                break
            if 'resnum' in extraction_target:
                extraction_target['thread'] = int(self.regex['thread'].findall(post)[0])
        for (key, value) in extraction_target.items():
            if value:
                post_items[key] = value
        return post_items

    def _parse(self, html):
        posts = defaultdict(dict)
        for post in self._extract_articles(html):
            post_items = self._extract_items(post)
            if not post_items:
                continue
            _id = post_items.pop('id')
            posts[_id].update(post_items)
            if not self.fast:
                posts[_id]['time'] = self._to_unixtime(posts[_id]['date'])

            if 'q1' in posts[_id]:
                posts[_id]['q1'] = '\n'.join(posts[_id]['q1'])
                if posts[_id].get('text') and self.fast is False:
                    text, posts = self._link_by_quote(posts[_id]['text'], _id, posts)
                    posts[_id]['text'] = text
                if 'q2' in posts[_id]:
                    posts[_id]['q2'] = '\n'.join(posts[_id]['q2'])
            if 'text' in posts[_id]:
                text = '\n'.join(posts[_id]['text']).rstrip()
                posts[_id]['text'] = self._delete_quote_link(text)
            if self.url is False:
                posts[_id] = self._delete_anchor_tag(posts[_id])
        return posts

    def to_dict(self, html, **args):
        """
        Param:
            <str> html
        Return:
            <dict <str>> json_log
        """
        if 'usamin_detail' in args:
            self.usamin_detail = args['usamin_detail']
        site = self._identify_site(html)
        self.regex = REGEX[site]
        html = self._cleansing(html, site)
        return self._parse(html)

    def to_json(self, html, **args):
        """
        Param:
            <str> html
        Return:
            <str> json_log
        """
        return json.dumps(self.to_dict(html, **args))
