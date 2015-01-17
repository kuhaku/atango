# -*- coding: utf-8 -*-
from nose.tools import assert_equals
import os
import tempfile
import shutil
from lib import file_io

tempdir = tempfile.mkdtemp()

CFG = ''
ASSERT_CFG = "{'DEFAULT': <Section: DEFAULT>}"
JSON = '{"mami": "pai"}'
TXT = ['mami', 'pai', 'mamipai']
ASSERT_TXT = "['mami', 'pai', 'mamipai']"
EXAMPLE_FILENAMES = ('example.cfg', 'example.json', 'example.txt')
EXAMPLE_PATHS = [os.path.join(tempdir, ex) for ex in EXAMPLE_FILENAMES]
EXAMPLES = dict(zip(EXAMPLE_PATHS, (CFG, JSON, '\n'.join(TXT))))
TEST_DATA = dict(zip(EXAMPLE_PATHS, (ASSERT_CFG, JSON.replace('"', "'"), ASSERT_TXT)))


def setup():
    for (example_path, content) in EXAMPLES.items():
        with open(example_path, 'w') as fd:
            fd.write(content)


def teardown():
    shutil.rmtree(tempdir)


def test_read_text_file():
    filename = tempfile.mkstemp()[1]
    try:
        with open(filename, 'w', encoding='utf8') as fd:
            fd.write('マミさん')

        got = file_io.read_text_file(filename, 'utf8')
        assert_equals(got, 'マミさん')

        got = file_io.read_text_file(filename)
        assert_equals(got, 'マミさん')
    finally:
        os.remove(filename)


def test_read():
    for (example_path, content) in TEST_DATA.items():
        actual = file_io.read(example_path)
        assert_equals(str(actual), content)
