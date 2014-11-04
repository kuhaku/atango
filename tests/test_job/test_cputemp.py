# -*- coding: utf-8 -*-
from nose.tools import assert_true, assert_false
from unittest.mock import patch
from job import cputemp


class test_CpuTemperatureChecker(object):

    def __init__(self):
        self.checker = cputemp.CpuTemperatureChecker()

    def test_get_mac_temperature(self):
        actual = self.checker.get_mac_temperature()
        assert_true(isinstance(actual, float))
        assert_true(actual > 0)

    def test_run(self):
        with patch('job.cputemp.misc.command') as cmd_patcher:
            cmd_patcher.return_value = (True, 'CPU temp: 100.0°C  ▁▂▃▅▆▇', None)
            with patch('job.cputemp.platform.system') as platform_patcher:
                platform_patcher.return_value = 'Darwin'

                cputemp.THRESHOLD = 80
                actual = self.checker.run()
                assert_true(actual)

                cputemp.THRESHOLD = 100
                actual = self.checker.run()
                assert_true(actual)

                cputemp.THRESHOLD = 1000
                actual = self.checker.run()
                assert_false(actual)
