# -*- coding: utf-8 -*-
from lib import app, misc, normalize


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


class ResponseGenerator(app.App):

    @staticmethod
    def _random_choice(text):
        return misc.choice(RESPONSES)

    def respond(self, text, screen_name=None, user='貴殿'):
        text = normalize.normalize(text)
        METHODS = (
            self._random_choice,  # Randomly
        )
        for method in METHODS:
            response = method(text)
            if response:
                break
        if not response:
            response = 'ああ(;´Д`)'
        return response
