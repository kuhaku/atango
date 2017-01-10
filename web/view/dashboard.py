import glob
from flask import Blueprint, Markup, render_template
from lib import misc
from job.cputemp import CpuTemperatureChecker

app = Blueprint('dashboard', __name__, template_folder='templates')


@app.route("/dashboard/")
def dashboard():
    def is_duplicate_launch():
        result = misc.command('pgrep -fl python|grep "atango.py -j twitter_respond"', True)
        return bool(result[1])

    def cpu_usage():
        result = misc.command("ps aux|awk '{ m+=$3 } END{ print m }'", True)
        return result[1].rstrip()

    def mem_usage():
        result = misc.command("ps aux|awk '{ m+=$4 } END{ print m }'", True)
        return result[1].rstrip()

    def read_log(path):
        result = misc.command(['cat', path])
        return result[1].rstrip().splitlines()

    heartbeat = 'いるよ！ヽ(´ー｀)ノ' if is_duplicate_launch() else 'ｼﾎﾞﾘ(;´Д`)'
    log = []
    for logfile in glob.glob('/work/atango/logs/*.log'):
        lines = read_log(logfile)
        log.append('<h2>%s</h2>' % logfile)
        log.append('<pre>')
        log += lines[-30:]
        log.append('</pre>')
    return render_template('dashboard.html', heartbeat=heartbeat,
                           log=Markup('\n'.join(log)),
                           cpuusage=cpu_usage(), memusage=mem_usage())
