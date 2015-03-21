from collections import defaultdict, Counter
from datetime import datetime, timedelta
from flask import Blueprint, render_template, Markup
from lib import kuzuha
from . import get_unixtime, parse_log, parse_time

app = Blueprint('sov', __name__, template_folder='templates')
WARATA_EXPS = ('ﾜﾗﾀ', 'ワラタ', 'わらた', '笑った', 'わらった', '笑いした', '笑いました',
               '笑える', '笑えて')


def get_log():
    date_range = kuzuha.build_yesterday_filter()
    posts = kuzuha.search('', _filter=date_range, sort=[('dt', 'asc')], _id=True)
    return list(posts)


def to_map(posts):
    return {int(post['_id']): post['_source'] for post in posts}


def join_posts(post_ids, posts):
    joined = ''
    for post_id in post_ids:
        joined += '<hr>\n%s\n' % parse_log(posts[post_id])
    return Markup(joined)


@app.route("/sov/latest")
def sov():
    yesterday_dt = datetime.today() - timedelta(days=1)
    yesterday = datetime.strftime(yesterday_dt, '%Y%m%d')

    posts = get_log()
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
                mentioned_post = kuzuha.get_log_by_id(post['quote'])['_source']
                mentioned_post_unixtime = get_unixtime(mentioned_post['dt'])
            response_timedelta = post['unixtime'] - mentioned_post_unixtime
            response_timedeltas[response_timedelta].append(post_id)

            # 最多ワラタ
            if post.get('text'):
                text = post['text']
                if any(warata in text for warata in WARATA_EXPS):
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
        most_warata_posts += '<hr>\n%s\n' % parse_log(posts[post_id])
    most_warata_posts = Markup(most_warata_posts)

    # 最多レス獲得賞
    most_mentioned = max(mentions)
    most_mentioned_posts = join_posts(mentions[most_mentioned], posts)

    # 最長ストッパー賞
    longest_stopped = max(stop_counter)
    longest_stopped_posts = join_posts(stop_counter[longest_stopped], posts)
    longest_stopped = parse_time(longest_stopped)

    # 最速レス賞
    fastest_res = min(response_timedeltas)
    fastest_res_posts = join_posts(response_timedeltas[fastest_res], posts)
    fastest_res = parse_time(fastest_res)

    # 最遅レス賞
    slowest_res = max(response_timedeltas)
    slowest_res_posts = join_posts(response_timedeltas[slowest_res], posts)
    slowest_res = parse_time(slowest_res)

    return render_template('sov.html', dt=yesterday,
                           num_most_warata=most_warata, most_warata_posts=most_warata_posts,
                           num_most_mentioned=most_mentioned, most_mentioned=most_mentioned_posts,
                           longest_stopped=longest_stopped, longest_stopper=longest_stopped_posts,
                           fastest_res=fastest_res, fastest_res_post=fastest_res_posts,
                           slowest_res=slowest_res, slowest_res_post=slowest_res_posts)
