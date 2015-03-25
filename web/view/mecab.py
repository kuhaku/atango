import os
import re
from subprocess import Popen
import jctconv
import MeCab
from flask import Blueprint, render_template, request
from lib import misc
from lib.nlp import mecab

app = Blueprint('mecab', __name__, template_folder='templates')
re_katakana = re.compile('^[ァ-ヺー]+$')
re_symbol = re.compile("[（）＜＞＊「」、。＝〜!！\?？…・\s]")
katakana = {chr(i) for i in range(12449, 12449+90)}
hiragana = {chr(i) for i in range(12353, 12353+86)}

PARTS_OF_SPEECH = (
    '名詞,一般名詞',
    '名詞,サ変',
    '名詞,固有名詞',
    '名詞,名',
    '名詞,姓',
    '名詞,人名一般',
    '名詞,組織',
    '名詞,地域',
    '名詞,形容動詞語幹',
    '名詞,接尾-一般',
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
    '動詞,五段ラ行基本',
    'フィラー',
)
DIC_POS = (
    ["", "1285", "1285", "", "名詞", "一般", "*", "*", "*", "*", "", "", "", "", ""],
    ["", "1283", "1283", "", "名詞", "サ変接続", "*", "*", "*", "*", "", "", "", "", ""],
    ["", "1288", "1288", "", "名詞", "固有名詞", "一般", "*", "*", "*", "", "", "", "", ""],
    ["", "1291", "1291", "", "名詞", "固有名詞", "人名", "名", "*", "*", "", "", "", "", ""],
    ["", "1290", "1290", "", "名詞", "固有名詞", "人名", "姓", "*", "*", "", "", "", "", ""],
    ["", "1289", "1289", "", "名詞", "固有名詞", "人名", "一般", "*", "*", "", "", "", "", ""],
    ["", "1292", "1292", "", "名詞", "固有名詞", "組織", "*", "*", "*", "", "", "", "", ""],
    ["", "1293", "1293", "", "名詞", "固有名詞", "地域", "一般", "*", "*", "", "", "", "", ""],
    ["", "1287", "1287", "", "名詞", "形容動詞語幹", "*", "*", "*", "*", "", "", "", "", ""],
    ["", "1298", "1298", "", "名詞", "接尾", "一般", "*", "*", "*", "", "", "", "", ""],
    ["", "1300", "1300", "", "名詞", "接尾", "助数詞", "*", "*", "*", "", "", "", "", ""],
    ["", "1301", "1301", "", "名詞", "接尾", "形容動詞語幹", "*", "*", "*", "", "", "", "", ""],
    ["", "1306", "1306", "", "名詞", "代名詞", "一般", "*", "*", "*", "", "", "", "", ""],
    ["", "1295", "1295", "", "名詞", "数", "*", "*", "*", "*", "", "", "", "", ""],
    ["", "5", "5", "", "記号", "一般", "*", "*", "*", "*", "", "", "", "", ""],
    ["", "3", "3", "", "感動詞", "*", "*", "*", "*", "*", "", "", "", "", ""],
    ["", "1281", "1281", "", "副詞", "一般", "*", "*", "*", "*", "", "", "", "", ""],
    ["", "1282", "1282", "", "副詞", "助詞類接続", "*", "*", "*", "*", "", "", "", "", ""],
    ["", "19", "19", "", "形容詞", "自立", "*", "*", "形容詞・アウオ段", "基本形", "", "", "", "", ""],
    ["", "560", "560", "", "接頭詞", "名詞接続", "*", "*", "*", "*", "", "", "", "", ""],
    ["", "557", "557", "", "接頭詞", "形容詞接続", "*", "*", "*", "*", "", "", "", "", ""],
    ["", "772", "772", "", "動詞", "自立", "*", "*", "五段・ラ行", "基本形", "", "", "", "", ""],
    ["", "2", "2", "", "フィラー", "*", "*", "*", "*", "*", "", "", "", "", ""],
)
DEFALUT_FORMAT = ' -F%m\\t%phl,%phr,%c,%H\\n --eos-format=EOS\\t%pC,%pn,%pc\\n '


def is_updating_dic_now():
    result = misc.command('pgrep -fl bash|grep "mecab_update.sh"', True)
    return bool(result[1].splitlines())

def update_dic():
    Popen(['bash', '/work/atango/util/mecab/mecab_update.sh'])

def get_yomi(word):
    word = re_symbol.sub('', word)
    katakana = jctconv.hira2kata(word)
    if re_katakana.match(katakana):
        return katakana
    else:
        katakana = ''.join(mecab.to_yomi(word))
        if re_katakana.match(katakana):
            return katakana
    return '*'

def get_dicdir():
    result = misc.command('mecab-config --dicdir', True)
    return result[1].strip()

@app.route("/mecab/", methods=['GET', 'POST'])
def mecab_maintenance():
    ma_result = ''
    term_added_message = ''
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
            for (i, pos_idx) in enumerate(PARTS_OF_SPEECH):
                if pos_idx == input_pos:
                    pos = DIC_POS[i].copy()
                    pos[0] = term
                    pos[10] = request.form['lemma'] or term
                    pos[3] = 0
                    yomi = request.form['yomi'] or get_yomi(term)
                    pos[11] = pos[12] = yomi
                    pos.append('MA')
                    pos = map(str, pos)
                    output = ','.join(pos)
                    dicpath = os.path.join(get_dicdir(), 'original', 'manual.csv')
                    with open(dicpath, 'a+', encoding='utf8') as fd:
                        fd.write(output + '\n')
                    term_added_message = 'Added %s' % output
                    break
        elif request.form.get('update'):
            update_dic()
    return render_template('mecab.html', ma_result=ma_result,
                           term_added_message=term_added_message,
                           updating_dic_now=updating_dic_now,
                           PARTS_OF_SPEECH=PARTS_OF_SPEECH)
