from collections import defaultdict, Counter
from datetime import datetime, timedelta
from flask import Blueprint, render_template, Markup
from lib import kuzuha
from . import get_unixtime, parse_log, parse_time

app = Blueprint('sov', __name__, template_folder='templates')


def get_log():
    date_range = kuzuha.build_yesterday_filter()
    posts = kuzuha.search('', _filter=date_range, sort=[('dt', 'asc')], _id=True)
    return list(posts)

def to_map(posts):
    return {int(post['_id']): post['_source'] for post in posts}

#def get_root_post()

@app.route("/sov/latest")
def sov():
    yesterday_dt = datetime.today() - timedelta(days=1)
    yesterday = datetime.strftime(yesterday_dt, '%Y%m%d')
    stopper_maximum = ('', 0)
    res_minimum = ('', 1 << 32)
    res_maximum = ('', 0)
    mentions = defaultdict(list)

    posts = get_log()
    posts = to_map(posts)
    prev_post = sorted(posts.items())[0][1]
    prev_post['unixtime'] = get_unixtime(prev_post['dt'])
    id2time_table = {}
    warata_counter = Counter()

    for (post_id, post) in sorted(posts.items())[1:]:
        post['id'] = post_id
        post['unixtime'] = get_unixtime(post['dt'])
        id2time_table[post_id] = post['unixtime']

        # 最長ストッパー
        previous_timedelta = post['unixtime'] - prev_post['unixtime']
        if previous_timedelta > stopper_maximum[1]:
            stopper_maximum = (prev_post, previous_timedelta)

        if post.get('quote', 0) in id2time_table:
            response_timedelta = post['unixtime'] - id2time_table[post['quote']]
            # 最速レス
            if response_timedelta < res_minimum[1]:
                res_minimum = (post, response_timedelta)
            # 最遅レス
            elif response_timedelta > res_maximum[1]:
                res_maximum = (post, response_timedelta)

            # 最多ワラタ
            if post.get('text'):
                text = post['text']
                if any(w in text for w in ('ﾜﾗﾀ', 'ワラタ', 'わらた', '笑った', 'わらった')):
                    warata_counter[post['quote']] += 1

        # 最多レス
        if 'quoted_by' in post:
            num_mentioned = len(post['quoted_by'])
            mentions[num_mentioned].append(post)

        prev_post = post

    # 最多ワラタ獲得賞
    most_warata_posts = ''
    num_most_warata = 0
    for (post_id, count) in warata_counter.most_common():
        if count < num_most_warata:
            break
        num_most_warata = count
        most_warata_posts += '<hr>\n%s\n' % parse_log(posts[post_id])
    most_warata_posts = Markup(most_warata_posts)

    # 最多レス獲得賞
    most_mentioned = sorted(mentions.keys())[-1]
    most_mentioned_posts = ''
    for article in mentions[most_mentioned]:
        most_mentioned_posts += '<hr>\n%s\n' % parse_log(article)
    most_mentioned_posts = Markup(most_mentioned_posts)

    # 最長ストッパー賞
    longest_stopper = Markup(parse_log(stopper_maximum[0]))
    longest_stopped = parse_time(stopper_maximum[1])

    # 最速レス賞
    fastest_res = parse_time(res_minimum[1])
    fastest_res_post = Markup(parse_log(res_minimum[0]))

    # 最遅レス賞
    slowest_res = parse_time(res_maximum[1])
    slowest_res_post = Markup(parse_log(res_maximum[0]))

    return render_template('sov.html', dt=yesterday,
                           num_most_warata=num_most_warata, most_warata_posts=most_warata_posts,
                           num_most_mentioned=most_mentioned, most_mentioned=most_mentioned_posts,
                           longest_stopped=longest_stopped, longest_stopper=longest_stopper,
                           fastest_res=fastest_res, fastest_res_post=fastest_res_post,
                           slowest_res=slowest_res, slowest_res_post=slowest_res_post)
