import random
import re
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from flask import Blueprint, render_template, Markup, request
from lib import kuzuha
from . import get_unixtime, parse_log, add_tag, add_res_button
from . import parse_time, parse_kuzuha_date, dt_to_ymd

app = Blueprint('sov', __name__, template_folder='templates')
WARATA_EXPS = ('ﾜﾗﾀ', 'ワラタ', 'わらた', '笑った', 'わらった', '笑いした', '笑いました',
               '笑える', '笑えて')
USAMIN_LINK = 'usamin.mine.nu/cgi/swlog?b=qwerty'
re_res = re.compile('qwerty.on.arena.ne.jp/cgi\-bin/bbs.cgi\?m=f&u=&d=30&c=900&ff=\d+.dat&s=')
re_thread = re.compile('qwerty.on.arena.ne.jp/cgi\-bin/bbs.cgi\?m=t&c=900&ff=\d+.dat&s=')


def get_log(target_dt):
    date_range = kuzuha.build_date_filter(target_dt, target_dt.replace(hour=23, minute=59))
    posts = kuzuha.search('', _filter=date_range, sort=[('dt', 'asc')], _id=True)
    return list(posts)


def to_map(posts):
    return {int(post['_id']): post['_source'] for post in posts}


def join_posts(post_ids, posts, add_res=False, use_usamin_link=False):
    joined = ''
    for post_id in post_ids:
        joined += '<hr>\n%s\n' % parse_log(posts[post_id])
        if add_res:
            joined += add_tag(add_child(posts[post_id]['quoted_by'], posts), 'pre')
    if use_usamin_link:
        joined = re_res.sub(USAMIN_LINK + '&id=', joined)
        joined = re_thread.sub(USAMIN_LINK + '&s=', joined)
    return Markup(joined)


def add_child(post_ids, posts):
    result = ''
    last_idx = len(post_ids) - 1
    for (i, post_id) in enumerate(post_ids):
        result += '└' if i == last_idx else '├'
        if post_id in posts:
            post = posts[post_id]
        else:
            post = kuzuha.get_log_by_id(post_id)['_source']
        dt = dt_to_ymd(post['dt'])
        res_link = add_res_button(post_id, dt).strip()
        title_text = '" title="%s">' % parse_kuzuha_date(post['dt'])
        result += res_link.replace('">', title_text) + ' '
        keisen = '  ' if i == last_idx else '│'
        if 'text' in post:
            result += post['text'].replace('\n', '\n' + keisen + '   ') + '\n'
    return result


def generate_report(target_dt):
    target_day = datetime.strftime(target_dt, '%Y%m%d')
    use_usamin_link = datetime.today() - target_dt >= timedelta(days=7)

    posts = get_log(target_dt)
    posts = to_map(posts)
    prev_post = posts[min(posts)]
    prev_post['unixtime'] = get_unixtime(prev_post['dt'])
    prev_post['id'] = min(posts)
    id2time_table = {}

    warata_counter = Counter()
    mentions = defaultdict(list)
    stop_counter = defaultdict(list)
    response_timedeltas = defaultdict(list)

    for (post_id, post) in sorted(posts.items())[1:]:
        post['id'] = post_id
        post['unixtime'] = get_unixtime(post['dt'])
        id2time_table[post_id] = post['unixtime']

        # 最長ストッパー
        previous_timedelta = post['unixtime'] - prev_post['unixtime']
        stop_counter[previous_timedelta].append(prev_post['id'])

        if 'quote' in post:
            # 最速レス & 最遅レス
            if post['quote'] in id2time_table:
                mentioned_post_unixtime = id2time_table[post['quote']]
            else:
                try:
                    mentioned_post = kuzuha.get_log_by_id(post['quote'])['_source']
                    if 'dt' not in mentioned_post:
                        continue
                except:
                    continue
                mentioned_post_unixtime = get_unixtime(mentioned_post['dt'])
            response_timedelta = post['unixtime'] - mentioned_post_unixtime
            response_timedeltas[response_timedelta].append(post_id)

            # 最多ワラタ
            if post.get('text'):
                if any(warata in post['text'] for warata in WARATA_EXPS):
                    warata_counter[post['quote']] += 1

        # 最多レス
        if 'quoted_by' in post:
            num_mentioned = len(post['quoted_by'])
            mentions[num_mentioned].append(post_id)

        prev_post = post

    # 最多ワラタ獲得賞
    most_warata_posts = ''
    most_warata = 0
    for (post_id, count) in warata_counter.most_common():
        if count < most_warata:
            break
        most_warata = count
        if post_id in posts:
            post = posts[post_id]
        else:
            post = kuzuha.get_log_by_id(post_id)['_source']
        most_warata_posts += '<hr>\n%s\n' % parse_log(post)
        most_warata_posts += add_tag(add_child(post['quoted_by'], posts), 'pre')
    if use_usamin_link:
        most_warata_posts = re_res.sub(USAMIN_LINK + '&id=', most_warata_posts)
        most_warata_posts = re_thread.sub(USAMIN_LINK + '&s=', most_warata_posts)
    most_warata_posts = Markup(most_warata_posts)

    # 最多レス獲得賞
    if mentions:
        most_mentioned = max(mentions)
        most_mentioned_posts = join_posts(mentions[most_mentioned], posts, True, use_usamin_link)
    else:
        most_mentioned = None
        most_mentioned_posts = None

    # 最長ストッパー賞
    if stop_counter:
        longest_stopped = max(stop_counter)
        longest_stopped_posts = join_posts(stop_counter[longest_stopped], posts, False,
                                           use_usamin_link)
        longest_stopped = parse_time(longest_stopped)
    else:
        longest_stopped = None
        longest_stopped_posts = None

    # 最速レス賞
    if response_timedeltas:
        fastest_res = min(response_timedeltas)
        fastest_res_posts = join_posts(response_timedeltas[fastest_res], posts, False, use_usamin_link)
        fastest_res = parse_time(fastest_res)
    else:
        fastest_res = None
        fastest_res_posts = None

    # 最遅レス賞
    if response_timedeltas:
        slowest_res = max(response_timedeltas)
        slowest_res_posts = join_posts(response_timedeltas[slowest_res], posts, False, use_usamin_link)
        slowest_res = parse_time(slowest_res)
    else:
        slowest_res = None
        slowest_res_posts = None

    return render_template('sov.html', dt=target_day,
                           num_most_warata=most_warata, most_warata_posts=most_warata_posts,
                           num_most_mentioned=most_mentioned, most_mentioned=most_mentioned_posts,
                           longest_stopped=longest_stopped, longest_stopper=longest_stopped_posts,
                           fastest_res=fastest_res, fastest_res_post=fastest_res_posts,
                           slowest_res=slowest_res, slowest_res_post=slowest_res_posts)


@app.route("/sov/latest")
def sov_latest():
    yesterday_dt = datetime.today() - timedelta(days=1)
    return generate_report(yesterday_dt)


@app.route("/sov/", methods=['GET'])
def sov():
    dt = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    if request.args.get('date'):
        if request.args['date'] == 'random':
            oldest_timedelta = dt - datetime(2005, 3, 11)
            rand_timedelta = timedelta(days=random.randint(0, oldest_timedelta.days))
            dt = dt - rand_timedelta
        else:
            dt = datetime.strptime(request.args['date'], '%Y%m%d')
    return generate_report(dt)
