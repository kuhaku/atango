# -*- coding: utf-8 -*-
from encodings.aliases import aliases
import nkf

all_encodings = set(aliases.values()) | set(aliases.keys())


def normalize_encoding(encoding):
    encoding = encoding.lower()
    if encoding in ('windows-31j', 'shift-jis', 'shift_jis', 'x-sjis', 'sjis'):
        return 'cp932'
    return encoding


def decode(text, encoding=None, *args):
    if not encoding or encoding in ('ISO-8859-1', 'iso-8859-1'):
        encoding = nkf.guess(text)
        if encoding in ('BINARY', 'ISO-8859-1'):
            encoding = 'utf8'
    encoding = normalize_encoding(encoding)
    if not encoding in all_encodings:
        return nkf.nkf('-w', text).decode('utf8')
    return text.decode(encoding, *args)
