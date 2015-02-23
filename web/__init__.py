# -*- coding: utf-8 -*-
import glob
from flask import Flask, request, make_response, Markup, render_template
from lib import normalize, misc
from job.reply import Reply
from job.cputemp import CpuTemperatureChecker

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


@app.route("/dashboard/")
def dashboard():
    def is_duplicate_launch():
        result = misc.command('pgrep -fl python|grep "atango.py -j crawler"', True)
        return bool(result[1].splitlines())

    def cpu_usage():
        result = misc.command("ps aux|awk '{ m+=$3 } END{ print m }'", True)
        return result[1].rstrip()

    def mem_usage():
        result = misc.command("ps aux|awk '{ m+=$4 } END{ print m }'", True)
        return result[1].rstrip()

    alive = 'still aliveヽ(´ー｀)ノ' if is_duplicate_launch() else 'しんだよ(´Д`)'
    temp = CpuTemperatureChecker().get_mac_temperature()
    log = []
    for logfile in glob.glob('/work/atango/logs/*.log'):
        if logfile.endswith('cputemp.log'):
            continue
        with open(logfile, 'r') as fd:
            lines = fd.read().splitlines()
        log.append('<h3>%s</h3>' % logfile)
        log.append('<pre>')
        log += lines[-20:]
        log.append('</pre>')
    return render_template('dashboard.html', alive=alive, temp=temp, log=Markup('\n'.join(log)),
                           cpuusage=cpu_usage(), memusage=mem_usage())



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
