# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime


def format_date_time(value, date_format):
    if isinstance(value, datetime):
        return value.strftime(date_format)
    else:
        return datetime.strptime(value, date_format)


def to_unicode(s, encoding='utf-8'):
    if isinstance(s, unicode):
        return s
    elif isinstance(s, str):
        return s.decode('utf-8')
    return unicode(s)
