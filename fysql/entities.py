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
        else:
            self._value = '{0}{1}{0}.{0}{2}{0} AS {3}'.format(self.quote, column_table, column_name, column_alias)

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

class SQLJoin(SQLEntity):
    """
        SQLJoin: represents a sql join
    """
    def __init__(self, join, table, left, right):
        self._value = '{0} JOIN {1} ON {2}={3}'.format(join, table, left, right)

class SQLCondition(SQLEntity):
    """
        SQLCondition: represents a SQL condition
    """
    def __init__(self, left, operator, right):
        escape = False

        if isinstance(left, SQLCondition):
            left  = unicode(left)
        elif hasattr(left, 'column'):
            escape = left

        if isinstance(right, SQLCondition):
            right = unicode(right)
        else:
            if isinstance(right, list):
                right = '({0})'.format(','.join(map(left.escape, right)))
            elif not hasattr(right, 'column'):
                right = left.escape(right)
                
            if not escape and hasattr(right, 'column'):
                left = right.escape(left)


        self._value = '{0} {1} {2}'.format(unicode(left), operator, unicode(right))

    def __and__(self, other):
       self._value = '({0}) AND ({1})'.format(self._value, unicode(other))
       return self

    def __or__(self, other):
       self._value =  '({0}) OR ({1})'.format(self._value, unicode(other))
       return self

    def __invert__(self):
       self._value = 'NOT({0})'.format(self._value)
       return self