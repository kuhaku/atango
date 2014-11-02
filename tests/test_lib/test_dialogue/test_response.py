# -*- coding: utf-8 -*-
from nose.tools import nottest, assert_true, assert_false, assert_equals
from lib.dialogue import response
from lib import web

class test_ResponseGenerator(object):

    def __init__(self):
        self.resgen = response.ResponseGenerator()

    def test_random_choice(self):
        actual = self.resgen._random_choice()
        assert_true(actual)
        assert_true(isinstance(actual, str))

    def test__validate_query(self):
        query = ['私', '殺す', '思い出', '']
        actual = self.resgen._validate_query(query)
        desired = set(['私*', '殺す', '思い出'])
        assert_equals(set(actual), desired)

    def test__is_valid_post(self):
        assert_true(self.resgen._is_valid_post('マミさん'))
        assert_false(self.resgen._is_valid_post('はい'))
        assert_false(self.resgen._is_valid_post('きええええ'*200))

    @nottest
    def test__choice_res(self):
        html = web.open_url('http://usamin.mine.nu/cgi/swlog?b=qwerty&s=18146945')
        actual = self.resgen._choice_res(html, 'マミさん', False)
        desired = 'でもあの人悪党なんだろうなぁと思うとなんか(;´Д`)'
        assert_equals(actual, desired)

    @nottest
    def test__extract_response_by_search(self):
        actual = self.resgen._extract_response_by_search(['マミさん', 'おっぱい'], False)
        desired = 'ソウルジェムプリンがいいな(;´Д`)カラメルソースかき混ぜて濁らせるの'
        assert_equals(actual, desired)

    @nottest
    def test__extract_response_from_log(self):
        pass

    @nottest
    def test_respond(self):
        """
        actual = self.resgen.respond('マミさんって何？')
        print(actual)
        assert_true(actual.startswith('マミさん'))
        time.sleep(0.5)
        actual = self.resgen.respond('誰がかわいい？')
        print(actual)
        assert_true('かわいい' in actual)
        """
