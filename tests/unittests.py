#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import sys
import os

root_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
sys.path.append(root_path)

import itmm_schedule_checker

class Test_itmm_schedule_checker(unittest.TestCase):
    def test_WnenDifferentColorsInDateString(self):
        self.parser = itmm_schedule_checker.SchedulePageParser()
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

    def test_WhenGetContent(self):
        self.parser = itmm_schedule_checker.SchedulePageParser(
                                       itmm_schedule_checker.content_div_style)
        with open('schedule_webpage.html', encoding='utf-8') as file:
            html = file.read()
        with open('plain_content.txt', encoding='utf-8') as file:
            content = file.read()

        self.parser.feed(html)

        self.assertEqual(self.parser.content, content)

    def test_keywords_highlight(self):
        keywords = ("381606",)
        original_html = ('<p>Не состоятся занятия у групп: '
        '1) группа 1381407-3(а0837-2): 17 ноября занятия по  РЯиДР и ИТвИД, '
        '2) 381603м4: 16 ноября занятия по ПиЭВвИТ, '
        '3) 381606м2!: 17 ноября занятия по ИТвПНП</p>')

        html = itmm_schedule_checker.keywords_highlight(original_html, keywords)

        self.assertEqual(html,('<p>Не состоятся занятия у групп: '
        '1) группа 1381407-3(а0837-2): 17 ноября занятия по  РЯиДР и ИТвИД, '
        '2) 381603м4: 16 ноября занятия по ПиЭВвИТ, '
        '3) <span style="font-size:150%; font-weight:bold; color:#6f0035;">'
        '381606</span>м2!: 17 ноября занятия по ИТвПНП</p>'))

if __name__ == '__main__':
    unittest.main()
