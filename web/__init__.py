# -*- coding: utf-8 -*-
from flask import Flask, render_template
import sys
sys.path.append('/work/atango/web')
sys.path.append('/work/atango')
from view import api, dashboard, now_or_past, sov, mecab, ma

app = Flask(__name__)
for module in (api, dashboard, now_or_past, sov, mecab, ma):
    app.register_blueprint(getattr(module, 'app'))


@app.route("/")
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
