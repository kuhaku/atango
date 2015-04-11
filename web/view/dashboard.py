import glob
from flask import Blueprint, Markup, render_template
from lib import misc
from job.cputemp import CpuTemperatureChecker

app = Blueprint('dashboard', __name__, template_folder='templates')


@app.route("/dashboard/")
def dashboard():
    def is_duplicate_launch():
        result = misc.command('pgrep -fl python|grep "atango.py -j swcrawler"', True)
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
        log.append('<h2>%s</h2>' % logfile)
        log.append('<pre>')
        log += lines[-20:]
        log.append('</pre>')
    return render_template('dashboard.html', alive=alive, temp=temp, log=Markup('\n'.join(log)),
                           cpuusage=cpu_usage(), memusage=mem_usage())
