# -*- coding: utf-8 -*-
import re

re_url = re.compile(u'(https?://[\w/\-@%\+\*\?\[\]\(\)#&;:!=\.,~]{1,2048})')
re_title = re.compile(u'(?<=<title>)(.+?)(?=<\/title>)', re.I)
re_html_tag = re.compile(r'<.*?>')
