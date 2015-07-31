# -*- coding: utf-8 -*-
import json
from datetime import datetime
from elasticsearch import Elasticsearch, helpers
from lib import kuzuha
from lib.db import redis
from lib.logger import logger

ONE_DAY = 60 * 60 * 24


class ElasticSearchUpdate(object):

    def __init__(self):
        self.es = Elasticsearch()
        self.db = redis.db('log')
        self.actions = []

    def find(self, post_id):
        record = self.db.get('qwerty:%s' % post_id)
        if record:
            record = record.decode('utf8')
            stored_body = json.loads(record)
            if 'dt' in stored_body:
                stored_body['dt'] = datetime.strptime(stored_body['dt'], '%Y-%m-%d-%H-%M-%S')
            return stored_body
        return {}

    def update(self, post_id, body, _op_type):
        self.actions.append({'_index': "qwerty", '_type': "log",
                             '_op_type': _op_type, '_id': post_id, '_source': body.copy()})
        if _op_type == 'update':
            b = self.find(post_id)
            b.update(body)
            body = b
        body['dt'] = body['dt'].strftime('%Y-%m-%d-%H-%M-%S')
        logger.debug('%s: %s' % (_op_type.upper(), body))
        self.db.setex('qwerty:%s' % post_id, json.dumps(body), ONE_DAY)

    def build_body(self, post, post_id):
        body = {}
        if 'quote' in post:
            quoted_post = self.find(post['quote'])
            if quoted_post and post_id not in quoted_post.get('quoted_by', []):
                quoted_by = quoted_post.get('quoted_by', [])
                quoted_by.append(post_id)
                quoted_by = list(set(quoted_by))
                self.update(post['quote'], {'doc': {'quoted_by': quoted_by}}, 'update')
            else:
                logger.debug('Not found post id: %s' % post['quote'])
        body['dt'] = datetime.strptime(post['date'], '%Y-%m-%d-%H-%M-%S')
        for idx in ('q1', 'q2', 'text', 'quote', 'quoted_by', 'author', 'to'):
            if idx in post:
                body[idx] = post[idx]
        return body

    def run(self):
        params = kuzuha.gen_params('', {'minute': 20})
        posts = kuzuha.get_log_as_dict('qwerty', params, url=True) or {}
        for (post_id, post) in posts.items():
            if 'date' not in post:
                continue
            stored_body = self.find(post_id)
            body = self.build_body(post, post_id)
            if body and body != stored_body:
                self.update(post_id, body, 'index')
            else:
                logger.debug('NO CHANGE: %s' % body)
        if self.actions:
            logger.info(helpers.bulk(self.es, self.actions))
            self.es.indices.refresh(index='qwerty')
