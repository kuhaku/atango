import itertools
from collections import Counter
from lib import kuzuha, regex, normalize
from lib.nlp import ngram, mecab


def get_longest_common_substring(logs):
    ngramer = ngram.Ngramer()
    ngrams = ngramer.to_ngrams(logs, 25, 9)
    ngrams = itertools.chain.from_iterable(ngrams)
    ngram_counter = Counter(ngrams)

    if not ngram_counter:
        return None

    messages = []
    prev_count = 0
    for (message, count) in ngram_counter.most_common(1000):
        if count < prev_count:
            break
        messages.append(message)
        prev_count = count
    return sorted(messages, key=lambda x: len(x), reverse=True)


def cleansing(text):
    text = text.strip()
    text = text.replace('\n', '')
    text = regex.re_a_tag.sub('', text)
    text = normalize.remove_emoticon(text)
    return normalize.normalize(text, repeat=3)


def respond(text):
    logs = kuzuha.search(mecab.extract_word(text))
    logs = [cleansing(log.get('text', '')) for log in logs]
    for message in get_longest_common_substring(''.join(logs)):
        yield message + '(;´Д`)'
