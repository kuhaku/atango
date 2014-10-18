# -*- coding: utf-8 -*-
######################################
#
# Library for retrieving web contents
#
######################################
import tempfile
import requests
from .misc import choice
from . import file_io, config


TIMEOUT = 15
USER_AGENTS = [  # from: http://techblog.willshouse.com/2012/01/03/most-common-user-agents/
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/31.0.1650.57 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9) AppleWebKit/537.71 (KHTML, like Gecko) '
    'Version/7.0 Safari/537.71',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/31.0.1650.57 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/31.0.1650.57 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/31.0.1650.57 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/31.0.1650.57 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.101 Safari/537.36',
]
DEFAULT_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip,deflate',
    'Accept-Language': 'ja,en-US;q=0.8,en;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'close',
    'DNT': '1',
    'Pragma': 'no-cache',
}
encoding_known_sites = config.read('site_encoding.json')


def open_url(url, referer=None, binary=False, params=None, post=False):
    if not referer:
        referer = url
    headers = DEFAULT_HEADERS.copy()
    headers.update({'Referer': referer, 'User-Agent': choice(USER_AGENTS)})
    opts = {'params': params, 'timeout': TIMEOUT, 'headers': headers}
    if post:
        r = requests.post(url, **opts)
    else:
        r = requests.get(url, **opts)
    if binary:
        return r.iter_content()
    return decode_content(r)


def decode_content(r):
    for (site, encoding) in encoding_known_sites.items():
        if site in r.url:
            return r.content.decode(encoding)
    if r.encoding in ('ISO-8859-1', None) :
        return file_io.decode_by_guessing(r.content)
    return r.content.decode(r.encoding)


def download(url, store_path=None):
    if not store_path:
        store_path = tempfile.mkstemp()[1]
    with open(store_path, 'wb') as fd:
        for chunk in open_url(url, binary=True):
            fd.write(chunk)
