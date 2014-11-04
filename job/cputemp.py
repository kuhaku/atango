# -*- coding: utf-8 -*-
import platform
from lib import app, misc

THRESHOLD = 80
MESSAGE_FORMAT = 'もう駄目だ(　ﾟДﾟ　)爆発する CPU Temperature: %.3f℃'


class CpuTemperatureChecker(app.App):

    def get_mac_temperature(self):
        cmd_result = misc.command('istats cpu temp', True)
        return float(cmd_result[1].split(' ')[2][:-2])

    def run(self):
        temperature = 0
        system = platform.system()
        if system == 'Darwin':  # 今はMacしか対応しない
            temperature = self.get_mac_temperature()
        if THRESHOLD <= temperature:
            return MESSAGE_FORMAT % temperature
