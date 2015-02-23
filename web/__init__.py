# -*- coding: utf-8 -*-
from flask import Flask, request, make_response
from job.reply import Reply
from lib import normalize, misc

app = Flask(__name__)


@app.route("/api/dialogue/")
def dialogue():
    _input = request.args.get('text')
    rep = Reply()
    response = rep.make_response(_input)
    text = normalize.remove_emoticon(response['text'])
    return text.strip()


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


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
