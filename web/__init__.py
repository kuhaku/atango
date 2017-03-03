# -*- coding: utf-8 -*-
from flask import Flask, render_template
import sys
sys.path.append('/work/atango/web')
sys.path.append('/work/atango')
from view import api, dashboard, now_or_past, sov, mecab, ma
from lib.logger import logger

app = Flask(__name__)
for module in (api, dashboard, now_or_past, sov, mecab, ma):
    app.register_blueprint(getattr(module, 'app'))
logger.enable_file_handler('/work/atango/logs/uwsgi_error.log')
app.debug = True
app.config['DEBUG'] = True


@app.route("/")
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
    app.run(host='0.0.0.0', port=5002, debug=True)
