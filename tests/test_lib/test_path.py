# -*- coding: utf-8 -*-
from nose.tools import assert_equals, nottest
import tempfile
import os
import shutil
from lib import path

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


@nottest
def test___basedir():
    pass


@nottest
def test___get_path(dirname):
    pass


@nottest
def test_datadir():
    pass


@nottest
def test_cfgdir():
    pass


@nottest
def test_logdir():
    pass


def test_read():
    for (example_path, content) in TEST_DATA.items():
        actual = path.read(example_path)
        assert_equals(str(actual), content)
