# -*- coding: utf-8 -*-
import platform
from lib import misc
from lib.logger import logger

THRESHOLD = 80
MESSAGE_FORMAT = 'もう駄目だ(　ﾟДﾟ　)爆発する CPU Temperature: %.2f℃'


class CpuTemperatureChecker(object):

    @staticmethod
    def get_mac_temperature():
        cmd_result = misc.command('istats cpu temp', True)
        return float(cmd_result[1].split(' ')[2][:-2])

    def run(self):
        temperature = 0
        system = platform.system()
        if system == 'Darwin':  # 今はMacしか対応しない
            temperature = self.get_mac_temperature()
        logger.info('CPU TEMP: %.2f℃' % temperature)
        if THRESHOLD <= temperature:
            return MESSAGE_FORMAT % temperature
