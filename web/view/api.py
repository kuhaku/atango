import json
from flask import Blueprint, request, make_response
from lib import normalize, misc, file_io
from lib.db import redis
from job.reply import Reply
from . import compute_id

app = Blueprint('api', __name__)
fwords = file_io.read('fwords.json')
TWO_WEEK = 60*60*24*14


@app.route("/api/dialogue/")
def dialogue():
    def explicit_fword(text):
        for (implicit, explicit) in fwords.items():
            text = text.replace(implicit, explicit)
        return text

    _input = request.args.get('text')
    _input = explicit_fword(_input)

    uid = compute_id(request)
    db = redis.db('twitter')
    user_info = db.get('user:%s' % uid)
    if user_info:
        user_info = json.loads(user_info.decode('utf8'))
        user_info['tweets'].append(_input)
    else:
        user_info = {'replies': [], 'tweets': [_input]}
    user_info.update({'screen_name': '貴殿', 'name': '貴殿'})

    rep = Reply()
    response = rep.make_response(_input, user_info)
    if len(user_info['replies']) >= 20:
        user_info['replies'].pop(0)
    if len(user_info['tweets']) >= 20:
        user_info['tweets'].pop(0)
    user_info['replies'].append(response['text'])
    db.setex('user:%s' % uid, json.dumps(user_info), TWO_WEEK)
    response['text'] = normalize.remove_emoticon(response['text'])
    response['text'] = response['text'].strip()
    return response['text']


@app.route("/api/speech_synthesis/")
def speech_synthesis():
    _input = request.args.get('text')
    _input = str(_input)
    misc.command('/bin/bash /work/atango/bin/ojtalk.sh %s -q' % _input, True)
    with open('/tmp/out.wav', 'rb') as fd:
        response = make_response(fd.read())
    response.headers['Content-Type'] = 'audio/wav'
    response.headers['Content-Disposition'] = 'attachment; filename=voice.wav'
    return response
