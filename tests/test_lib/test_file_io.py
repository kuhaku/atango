# -*- coding: utf-8 -*-
from nose.tools import assert_equals
import os
import tempfile
from lib import file_io


def test_decode_by_guessing():
    got = file_io.decode_by_guessing(u'マミさん'.encode('utf8'))
    assert_equals(got, u'マミさん')


def test_read_text_file():
    filename = tempfile.mkstemp()[1]
    with open(filename, 'w', encoding='utf8') as fd:
        fd.write('マミさん')

    got = file_io.read_text_file(filename, 'utf8')
    assert_equals(got, u'マミさん')

    got = file_io.read_text_file(filename)
    assert_equals(got, u'マミさん')

    os.remove(filename)
