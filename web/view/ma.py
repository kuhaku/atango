import re
from collections import Counter, defaultdict
from flask import Blueprint, render_template, Markup
from lib import kuzuha
from lib.nlp import mecab

app = Blueprint('ma', __name__, template_folder='templates')
re_japanese = re.compile('[ぁ-ゖァ-ヺー]+')


def count_words(sentence):
    m = mecab.MeCabWrapper()
    words = []
    for node in m.parse_to_node(sentence):
        if node.feature.startswith('名詞') and re_japanese.match(node.surface):
            words.append('%s,%s' % (node.surface, node.feature))
    return words


@app.route("/ma/")
def morphological_analysis():
    posts = kuzuha.search('', _filter=kuzuha.build_date_filter_by_range({'minutes': 120}))
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
    html = ''
    for (i, (word, count)) in enumerate(word_counter.most_common()):
        html += '<h3><a onclick="switch_display(%s)">%s</a></h3>\n' % (i, word)
        html += '<ul id="%s">\n' % i
        for line in word_contain_posts[word]:
            html += '<li>%s</li>\n' % line
        html += '</ul>\n'
    return render_template('ma.html', html=Markup(html))
