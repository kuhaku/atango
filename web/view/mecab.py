import os
import re
from subprocess import Popen
import jctconv
import MeCab
from flask import Blueprint, render_template, request
from lib import misc
from lib.nlp import mecab
from . import is_int_castable
from .mecab_term_entry import add_term

app = Blueprint('mecab', __name__, template_folder='templates')
re_katakana = re.compile('^[ァ-ヺー]+$')
re_symbol = re.compile("[（）＜＞＊「」、。＝〜!！\?？…・\s]")
katakana = {chr(i) for i in range(12449, 12449+90)}
hiragana = {chr(i) for i in range(12353, 12353+86)}

PARTS_OF_SPEECH = (
    '名詞,一般名詞',
    '名詞,サ変',
    '名詞,固有名詞',
    '名詞,姓',
    '名詞,名',
    '名詞,人名一般',
    '名詞,組織',
    '名詞,地域',
    '名詞,形容動詞語幹',
    '名詞,接尾-一般',
    '名詞,接尾-人名',
    '名詞,接尾-助数詞',
    '名詞,接尾-形容動詞語幹',
    '名詞,代名詞',
    '名詞,数',
    '記号,一般',
    '感動詞',
    '副詞,一般',
    '副詞,助詞類接続',
    '形容詞,アウオ基本形',
    '接頭詞,名詞接続',
    '接頭詞,形容詞接続',
    '連体詞',
    '動詞,五段ラ行基本',
    'フィラー',
    '動詞',
    '〜しい',
)
DEFALUT_FORMAT = ' -F%m\\t%phl,%phr,%c,%H\\n --eos-format=EOS\\t%pC,%pn,%pc\\n '


def get_yomi(word):
    word = re_symbol.sub('', word)
    katakana = jctconv.hira2kata(word)
    if re_katakana.match(katakana):
        return katakana
    katakana = ''.join(mecab.to_yomi(word))
    if re_katakana.match(katakana):
        return katakana
    return '*'


def get_dicdir():
    result = misc.command('mecab-config --dicdir', True)
    return os.path.join(result[1].strip(), 'original')


def delete_term(line):
    if line.endswith(',E'):
        filename = 'enamdict.csv'
    elif line.endswith(',NST'):
        filename = 'naist_jdic.csv'
    elif line.endswith(',W'):
        filename = 'wiki120121.csv'
    elif line.endswith(',MZ'):
        filename = 'mozc.csv'
    elif line.endswith(',N'):
        filename = 'nico_name.csv'
    elif line.endswith(',WPH'):
        filename = 'wp_hiragana.csv'
    dicfile = os.path.join(get_dicdir(), filename)
    misc.command("grep -v '%s' %s > %s.temp" % (line, dicfile, dicfile), True)
    misc.command("mv %s.temp %s" % (dicfile, dicfile), True)


def check_matrix(lid, rid):
    grep = "grep -e'^%s %s ' matrix.def" % (lid, rid)
    result = misc.command("cd %s; %s" % (get_dicdir(), grep), True)
    return result[1]


def edit_matrix(lid, rid, cost):
    if cost.lower() == 'max':
        cost = '32765'
    elif cost.lower() == 'min':
        cost = '-32765'
    if not all(is_int_castable(v) for v in (lid, rid, cost)):
        return '[ERROR] Invalid value'
    lid = int(lid)
    rid = int(rid)
    cost = int(cost)
    if lid >= 1316 or rid >= 1316 or abs(cost) > 32765:
        return '[ERROR] Invalid value'
    matrix_file = os.path.join(get_dicdir(), 'matrix.def')
    line_number = 1316 * lid + rid + 2
    command = "sed -e '%dc\\'$'\\n''%d %d %d' %s > /tmp/matrix" % (line_number, lid, rid, cost,
                                                                   matrix_file)
    misc.command(command, True)
    misc.command('mv -f /tmp/matrix %s' % matrix_file, True)
    return 'Success!'


def is_updating_dic_now():
    result = misc.command('pgrep -fl bash|grep "mecab_update.sh"', True)
    return bool(result[1].splitlines())


def search(query):
    query = query.replace('*', '\\*')
    query = query.replace('+', '\\+')
    result = misc.command("cd %s; ag '%s'" % (get_dicdir(), query), True)
    return result[1]


def update_dic():
    Popen(['bash', '/work/atango/util/mecab/mecab_update.sh'])


@app.route("/mecab/", methods=['GET', 'POST'])
def mecab_maintenance():
    ma_result = ''
    term_added_message = ''
    check_matrix_message = ''
    edit_matrix_message = ''
    search_result = ''
    updating_dic_now = is_updating_dic_now()

    if request.method == 'POST':
        if request.form.get('ma'):
            nbest = int(request.form.get('nbest'))
            mecab_arg = '-N %s' % nbest if nbest > 1 else ''
            tagger = MeCab.Tagger(DEFALUT_FORMAT + mecab_arg)
            text = jctconv.h2z(request.form.get('ma'))
            for line in text.splitlines():
                ma_result += line + '\n'
                if nbest > 2:
                    tagger.parseNBestInit(line)
                    for i in range(nbest):
                        result = tagger.next()
                        if result:
                            ma_result += result
                        else:
                            break
                else:
                    ma_result += tagger.parse(line)
        elif request.form.get('add') and request.form.get('term'):
            input_pos = request.form.get('pos')
            term = request.form.get('term')
            lemma = request.form['lemma'] or term
            yomi = request.form['yomi'] or get_yomi(term)
            term_added_message = add_term(input_pos, term, lemma, yomi)
        elif request.form.get('del') and request.form.get('del_line'):
            delete_term(request.form.get('del_line'))
        elif all(request.form.get(v) for v in ('chk_matrix', 'lid', 'rid')):
            check_matrix_message = check_matrix(request.form['lid'], request.form['rid'])
        elif all(request.form.get(v) for v in ('matrix', 'lid', 'rid', 'cost')):
            edit_matrix_message = edit_matrix(request.form.get('lid'), request.form.get('rid'),
                                              request.form.get('cost'))
        elif request.form.get('search') and request.form.get('search_query'):
            search_result = search(request.form.get('search_query'))
        elif request.form.get('update'):
            update_dic()
    return render_template('mecab.html', ma_result=ma_result,
                           term_added_message=term_added_message,
                           check_matrix_message=check_matrix_message,
                           edit_matrix_message=edit_matrix_message,
                           search_result=search_result,
                           updating_dic_now=updating_dic_now,
                           PARTS_OF_SPEECH=PARTS_OF_SPEECH)
