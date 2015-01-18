# -*- coding: utf-8 -*-
import re

re_url = re.compile('(https?://[a-zA-Z0-9_/\-@%\+\*\?\[\]\(\)#&;:!=\.,~]{3,2048})')
re_html_tag = re.compile('<[^<]+>')
re_a_tag = re.compile('<a[^<]+</a>', re.I)
