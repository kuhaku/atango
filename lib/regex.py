# -*- coding: utf-8 -*-
import re

re_url = re.compile('(https?://[\w/\-@%\+\*\?\[\]\(\)#&;:!=\.,~]{1,2048})')
re_html_tag = re.compile('<[^<]+>')
re_a_tag = re.compile('<a[^<]+</a>', re.I)
