import redis
from lib import file_io

setting = file_io.read('atango.json')['Redis']
manager = {}


def db(name):
    if name not in manager:
        info = setting[name]
        conn = redis.Redis(**info)
        conn.ping()
        manager[name] = conn
    return manager[name]
