# -*- coding: utf-8 -*-
"""
    fysql.entities
    ~~~~~~~~~~~~~~
    :copyright: (c) 2016 by Gasquez Florian
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals

class SQLEntity(object):
    """
        SQLEntity: basic sql entity 
    """
    quote     = ''

    def __init__(self, name):
        self._value = '{0}{1}{0}'.format(self.quote, name)

    def __unicode__(self):
        return self._value

class SQLColumn(SQLEntity):
    """
        SQLColumn: represents a column in a table
    """
    quote     = '`'

    def __init__(self, column_table, column_name, column_alias=False):
        if not column_alias:
            self._value = '{0}{1}{0}.{0}{2}{0}'.format(self.quote, column_table, column_name)

    def __unicode__(self):
        return self._value

class SQLTable(SQLEntity): 
    """
        SQLColumn: represents a table in a database
    """
    quote     = '`'

    def __init__(self, name, table_alias=False):
        if not table_alias:
            super(SQLTable, self).__init__(name)
