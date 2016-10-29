#!/usr/bin/env python3
"""
Schedule changes checker for http://itmm.unn.ru

Downloads schedule web-page (http://itmm.unn.ru/studentam/raspisanie),
parses it to extract changes, link to schedule file, time of last change,
downloads schedule file,
send all via email.

Script strongly depends on format of page.

Requires mail.py.

Recommended for use with cron.

Using: itmm_schedule_checker.py <from-email> <to-email>
"""

from urllib.request import urlopen
from urllib.parse import urlparse
from html.parser import HTMLParser
from datetime import datetime, date, time
import re
import os
import difflib

import mail


url = 'http://itmm.unn.ru/studentam/raspisanie'
content_div_style = "col-sm-8"
working_directory = os.path.expanduser("~/.itmm_schedule_checker")
datetimeformat = '%Y.%m.%d-%H.%M.%S'
html_template = """\
<html>
  <head></head>
  <body>
    {}
  </body>
</html>
"""
sendfilelink = True
senddatetime = False


def get_last(prefix):
    names = [name for name in os.listdir(working_directory)
             if name.startswith(prefix)]
    last = max(names,
        key=lambda n: datetime.strptime(n.split('_')[1][0:18], datetimeformat))
    path = os.path.join(working_directory, last)
    return path


class SchedulePageParser(HTMLParser):

    def __init__(self, content_div_style=None):
        self.content_div_style = content_div_style
        self.in_content_div = False
        self.in_master_p = False
        self.content = ''
        self.html_content = ''
        self.link = None
        self.datetime = None
        self.date = None
        self.time = None
        self.date_regexp = re.compile('[0-3]?[0-9]\.[0-1]?[0-9](\.201[0-9])?')
        self.time_regexp = re.compile('[0-2]?[0-9]:[0-5][0-9]')
        HTMLParser.__init__(self, strict=False)

    def handle_starttag(self, tag, attrs):
        if self.content_div_style:

            if self.in_content_div:
                attrsstr = ''
                for attr in attrs:
                    attrsstr += ' {0}="{1}"'.format(*attr)
                self.html_content += '<{}{}>'.format(tag, attrsstr)

            if tag == 'div':
                if not self.in_content_div:
                    for attr in attrs:
                        if (attr[0] == 'class' and
                                attr[1] == self.content_div_style):
                            self.in_content_div = True
                            self.div_level = 0
                            break
                else:
                    self.div_level += 1
        if self.in_master_p and tag == 'a' and not self.link:
            for attr in attrs:
                if attr[0] == 'href':
                    self.link = attr[1]

    def handle_data(self, data):
        if self.in_content_div:
            self.html_content += data

        if self.in_content_div or not content_div_style:
            self.content += data
            if "расписание магистров" in data.lower():
                self.in_master_p = True
            if self.in_master_p:
                date_match = self.date_regexp.search(data)
                if date_match:
                    date_tuple = tuple(int(str_num)
                                 for str_num in date_match.group(0).split('.'))
                    self.date = date(*tuple(reversed(date_tuple)))
                time_match = self.time_regexp.search(data)
                if time_match:
                    time_tuple = tuple(int(str_num)
                                 for str_num in time_match.group(0).split(':'))
                    self.time = time(*time_tuple)

    def handle_endtag(self, tag):
        if self.content_div_style and self.in_content_div:

            self.html_content += '</{}>'.format(tag)

            if tag == 'div':
                if self.div_level:
                    self.div_level -= 1
                else:
                    self.in_content_div = False
        if self.in_master_p and tag == 'p':
            self.in_master_p = False

    def feed(self, html):
        HTMLParser.feed(self, html)
        self.datetime = datetime.combine(self.date, self.time)


class HTMLtoPlainParser(HTMLParser):

    def __init__(self):
        self.content = ''
        HTMLParser.__init__(self, strict=False)

    def handle_data(self, data):
        self.content += data

    def feed(self, html):
        HTMLParser.feed(self, html)
        text = self.content
        self.content = ''
        return text


if __name__ == '__main__':
    # Script specific imports
    import sys
    # to do:
    # from argparse import ArgumentParser

    if len(sys.argv[1:]) != 2:
        print('Using: itmm_schedule_checker.py <from-email> <to-email>')
    else:
        now_str = datetime.now().strftime(datetimeformat)
        from_email, to_email = sys.argv[1:]

        # flags
        page_changed = False
        content_changed = False
        datetime_changed = False
        link_changed = False
        schedule_changed = False

        if not os.path.exists(working_directory):
            os.mkdir(working_directory)
            print('Working directory created.')

        if not os.listdir(working_directory):
            print('Working directory is empty, have no data to compare.')

            current_page_data = urlopen(url).read()
            current_html = current_page_data.decode('utf-8')
            parser_current = SchedulePageParser(content_div_style)
            parser_current.feed(current_html)
            pagefilename = 'page'+'_'+now_str+'.html'
            with open(os.path.join(working_directory, pagefilename),'wb') as f:
                f.write(current_page_data)
            origfn = os.path.basename(urlparse(parser_current.link).path)
            schedulefilename = '_'.join(('schedule', now_str, origfn))
            current_schedule_data = urlopen(parser_current.link).read()
            with open(os.path.join(working_directory,
                                   schedulefilename), 'wb') as f:
                f.write(current_schedule_data)

            msg = mail.make(from_email, to_email, 'Запуск мониторинга',
                            text = ('Первый запуск скрипта.\n'
                                    'Страница расписания: {}\n'
                                    'Файл расписания: {}\n'.format(url,
                                                         parser_current.link)))
            mail.send(msg)
            exit()

        current_page_data = urlopen(url).read()

        with open(get_last('page'), 'rb') as f:
            last_page_data = f.read()
        with open(get_last('schedule'), 'rb') as f:
            last_schedule_data = f.read()

        current_html = current_page_data.decode('utf-8')
        parser_current = SchedulePageParser(content_div_style)
        parser_current.feed(current_html)

        if last_page_data == current_page_data:
            current_schedule_data = urlopen(parser_current.link).read()
            if current_schedule_data != last_schedule_data:
                schedule_changed = True
            else:
                exit()
        else:
            page_changed = True

            pagefilename = 'page'+'_'+now_str+'.html'
            with open(os.path.join(working_directory, pagefilename),'wb') as f:
                f.write(current_page_data)

            last_html = last_page_data.decode('utf-8')
            parser_last = SchedulePageParser(content_div_style)
            parser_last.feed(last_html)
            current_schedule_data = urlopen(parser_current.link).read()

            if current_schedule_data != last_schedule_data:
                schedule_changed = True
            if parser_last.link != parser_current.link:
                link_changed = True
            if parser_last.content != parser_current.content:
                content_changed = True
            if parser_last.datetime != parser_current.datetime:
                datetime_changed = True

        htmltoplane = HTMLtoPlainParser()

        if schedule_changed:
            origfn = os.path.basename(urlparse(parser_current.link).path)
            schedulefilename = '_'.join(('schedule', now_str, origfn))
            with open(os.path.join(working_directory,
                                   schedulefilename), 'wb') as f:
                f.write(current_schedule_data)

        if content_changed:
            new_title_html = '<hr><p><b>Обновленное:</b></p>\n'
            old_title_html = '</br><p><b>Устаревшее:</b></p>\n'

            d = difflib.Differ()

            last_content_lns = parser_last.content.splitlines(True)
            current_content_lns = parser_current.content.splitlines(True)
            content_diff_lns = d.compare(last_content_lns, current_content_lns)
            content_new_lns = [s[2:] for s in content_diff_lns if s[:2] =='+ ']
            content_old_lns = [s[2:] for s in content_diff_lns if s[:2] =='- ']
            content_diff = (htmltoplane.feed(new_title_html)+
                            ''.join(content_new_lns)+
                            htmltoplane.feed(old_title_html)+
                            ''.join(content_old_lns))

            last_html_lns = last_html.splitlines(True)
            current_html_lns = current_html.splitlines(True)
            html_diff_lns = list(d.compare(last_html_lns, current_html_lns))
            html_new_lns = [s[2:] for s in html_diff_lns if s[:2] == '+ ']
            html_old_lns = [s[2:] for s in html_diff_lns if s[:2] == '- ']
            html_diff = (new_title_html+
                        '<div>'+''.join(html_new_lns)+'</div>'+
                         old_title_html+
                       '<div><strike>'+''.join(html_old_lns)+'</strike></div>')

        changes = []
        if schedule_changed:
            changes.append('файл')
        if content_changed:
            changes.append('контент')
        if link_changed and not schedule_changed:
            changes.append('ссылка')
        if (page_changed and
             not (content_changed or (link_changed and not schedule_changed))):
            changes.append('страница')
        changes = ', '.join(changes)

        subject = 'Изменения в расписании ({})'.format(changes)

        html_part = ('<p>Изменились: <b>{}</b></p>'.format(
                                        changes.replace(', ', '</b>, <b>')) +
                     '<p>Страница расписания: ' +
                     '<a href="{0}">{0}</a></p>\n'.format(url))
        attachment = None

        if sendfilelink or link_changed or schedule_changed:
            btags = ('', '')
            if schedule_changed or link_changed:
                btags = ('<b>', '</b>')
            html_part += ('<p>Файл расписания: ' +
                '{1}<a href="{0}">{0}</a>{2}</p>\n'.format(parser_current.link,
                                                           *btags))

        if senddatetime or datetime_changed:
            hrdtstr = parser_current.datetime.strftime('%H:%M %d.%m.%Y')
            html_part += ('<p>Время последней правки: '
                          '<b><a href="{0}">{0}</a></b></p>\n'.format(hrdtstr))

        text_part = htmltoplane.feed(html_part)

        if content_changed:
            text_part += '\n\n' + content_diff
            html_part += '<p></br> \n</br> \n</p>' + html_diff

        # trying to prevent message clipping by gmail
        text_part += '\n\n' + now_str
        html_part += '\n\n<p><font color="#cccccc">' + now_str + '</font></p>'

        if schedule_changed:
            attachment = {'data': current_schedule_data,
                          'name': origfn}

        html_part = html_template.format(html_part)
        msg = mail.make(from_email, to_email, subject,
                        text_part, html_part, attachment)
        mail.send(msg)
