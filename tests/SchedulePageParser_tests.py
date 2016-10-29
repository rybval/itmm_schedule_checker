#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import sys
import os
script_path = os.path.abspath('..')
sys.path.append(script_path)
import itmm_schedule_checker

class TestSchedulePageParser(unittest.TestCase):
    def setUp(self):
        self.parser = itmm_schedule_checker.SchedulePageParser()

    def test_WnenDifferentColorsInDateString(self):
        html = ('<p>Постоянное расписание магистров <strong>'
        '<a href="http://www.itmm.unn.ru/files/2016/08/Magistry_19102016.xls">'
        'здесь</a>&nbsp;</strong>'
         '(<span style="color: #ff0000"><strong>новое!</strong>'
         '</span> версия от <span style="color: #ff6600">19</span>'
         '<span style="color: #ff0000"><span style="color: #ff6600">.'
         '</span>10.2016 г. 17:20</span>)</p>')


        result = self.parser._prepareHTML(html)

        self.assertEqual(result,
                         ('<p>Постоянное расписание магистров '
                          '<a href="http://www.itmm.unn.ru/files/2016/08/Magistry_19102016.xls">'
                          'здесь</a>&nbsp;(новое! версия от 19.10.2016 г. '
                          '17:20)</p>'))


if __name__ == '__main__':
    unittest.main()