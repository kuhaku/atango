# -*- coding: utf-8 -*-
import signal
import sys
import traceback
import re
import os
from . import path, api, misc
from .logger import logger

TIME_LIMIT = 55
ATANGO_DIR = os.environ.get('ATANGO_HOME', '/work/atango/')
LOG_DIR = os.path.join(ATANGO_DIR, 'logs')

DYING_MESSAGE = (
    'ぎゃああああ！(;´Д`)しんでしまう！',
    'うおーっ！！\nわたしは　さけびごえを　あげ　ほのおの　なかへ\n'
    'ホップ　ステップ　ジャンプ…\n'
    'かーるいす！！\n'
    'わたしは　もえつきてしまった。',
    'いどのなかに　からだを　なげいれた。\n'
    'ふかい！！ どこまで　おちるんだ！！\n'
    'ドシーン！！　ギャーッ！！ \n'
    'いどは　おもっていたよりも　ふかかったようだ。\n'
    'わたしは…　からだじゅうの　ほねを　おってしんでしまった。',
    'わたしは　はなを　つまみ　あぶらのなかへとびこんだ。\nあづーっ！！\n'
    'わたしは　とけてしまった。\nああ！！　わたしは　ゾンビにも　なれないのか…。',
    'わたしは　あぶらに　たいまつを　ちかづけた。\n'
    'ほのおは　めらめらと　もえあがり　わたしが　もっていた\nたいまつに　'
    'ひが　うつってしまった！\nあつい！！　わたしは　もえつきてしまった。',
    'ざんねん！　わたしの　ぼうけんは　これで　おわってしまった！',
)
SYGTERM_MESSAGE = '\nぁ単語 received SIGTERM.'


class ForcedTermination(Exception):

    def __init__(self, reason='', response=None):
        self.reason = str(reason)
        self.response = response
        Exception.__init__(self, reason)


class App(object):

    def _gen_logfile_path(self, jobname):
        filename = jobname + '.log'
        return os.path.join(LOG_DIR, filename)

    def setup_logger(self, jobname):
        logpath = self._gen_logfile_path(jobname)
        logger.enable_file_handler(logpath)
        path.mkdir(LOG_DIR)

        if self.verbose:
            logger.enable_stream_handler()
        if self.debug:
            logger.enable_debug()
        else:
            logger.enable_twitter_handler()
        self.logger = logger

    def set_timer(self, timelimit):
        def overtime_handler(self, *args):
            message = 'exceeds %d seconds' % (TIME_LIMIT)
            raise TimeoutError(message)

        signal.setitimer(signal.ITIMER_REAL, timelimit)
        signal.signal(signal.SIGALRM, overtime_handler)

    def execute(self, func, *args, **kwargs):
        try:
            self.set_timer(TIME_LIMIT)
            return func(*args, **kwargs)
        except TimeoutError as e:
            error_description = str(e)
            err_msg = 'TimeoutError: %s' % (error_description)
            self.logger.warn(err_msg)
        except Exception as e:
            error_class = e.__class__.__name__
            error_description = str(e)
            err_msg = '%s: %s' % (error_class, error_description)
            self.logger.critical(err_msg)
            tb = traceback.extract_tb(sys.exc_info()[2])
            trace = traceback.format_list(tb)
            self.logger.warn('---- traceback ----')
            for line in trace:
                text = re.sub(r'\n\s*', ' ', line.rstrip())
                self.logger.warn(text)
            self.logger.warn('-------------------')
            return sys.exit(err_msg)

    def main(self, job):
        def sigkill_handler(self, *args):
            message = misc.choice(DYING_MESSAGE) + SYGTERM_MESSAGE
            raise ForcedTermination(message)

        signal.signal(signal.SIGTERM, sigkill_handler)
        try:
            self.run(job)
        except ForcedTermination as e:
            logger.warn('ぁ単語 received SIGTERM')
            twitter = api.Twitter()
            twitter.post(str(e))
