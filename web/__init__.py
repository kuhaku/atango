# -*- coding: utf-8 -*-
from flask import Flask
from view import api, dashboard, now_or_past

app = Flask(__name__)
for module in (api, dashboard, now_or_past):
    app.register_blueprint(getattr(module, 'app'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
