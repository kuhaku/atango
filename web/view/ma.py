import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from flask import Blueprint, render_template, Markup, request
from lib import kuzuha
from lib.nlp import mecab

app = Blueprint('ma', __name__, template_folder='templates')
re_japanese = re.compile('[ぁ-ゖァ-ヺー一-鿇]+')
re_hiragana = re.compile('[ぁ-ゖー]+')
re_katakana = re.compile('[ァ-ヺー]+')
DT_RANGE = {'range': {'dt': {}}}


def count_words(sentence):
    m = mecab.MeCabWrapper()
    words = []
    for node in m.parse_to_node(sentence):
        if node.feature.startswith('名詞') and re_japanese.match(node.surface):
            words.append('%s,%s' % (node.surface, node.feature))
    return words


def dump_all_words(words, posts):
    all_result = ''
    for (i, (word, count)) in enumerate(words.most_common()):
        all_result += '<h3><a onclick="switch_display(%s)">%s</a></h3>\n' % (i, word)
        all_result += '<ul id="%s">\n' % i
        for line in posts[word]:
            all_result += '<li>%s</li>\n' % line
        all_result += '</ul>\n'
    return all_result


def suspected_word(words, posts):
    suspects = ''
    for (i, (word, count)) in enumerate(words.most_common()):
        lemma = word.split(',')[0]
        if '非自立' in word or '接尾' in word or len(lemma) > 2:
            continue
        if len(lemma) == 1 or re_katakana.search(lemma):
            suspects += '<h3><a onclick="switch_display(\'s%s\')">%s</a></h3>\n' % (i, word)
            suspects += '<ul id="s%s">\n' % i
            for line in posts[word]:
                suspects += '<li>%s</li>\n' % line
            suspects += '</ul>\n'
    return suspects


@app.route("/ma/", methods=['GET', 'POST'])
def morphological_analysis():
    if request.method != 'POST':
        return render_template('ma.html')

    hours = int(request.form.get('hours'))
    now = datetime.now()
    start_dt = now - timedelta(hours=hours)
    end_dt = start_dt + timedelta(hours=1)
    dt_range = DT_RANGE.copy()
    dt_range['range']['dt']['from'] = start_dt.strftime('%Y-%m-%dT%H:%M:%S')
    dt_range['range']['dt']['to'] = end_dt.strftime('%Y-%m-%dT%H:%M:%S')
    posts = kuzuha.search('', field='text', _filter=dt_range, sort=[], size=10000)
    word_counter = Counter()
    word_contain_posts = defaultdict(list)
    for post in posts:
        if not post.get('text'):
            continue
        for line in post['text'].splitlines():
            words = Counter(count_words(line))
            word_counter += words
            for word in words:
                word_contain_posts[word].append(line)
    all_result = dump_all_words(word_counter, word_contain_posts)
    suspects = suspected_word(word_counter, word_contain_posts)
    return render_template('ma.html', all_result=Markup(all_result), suspects=Markup(suspects),
                           hours=hours)
