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

class SQLQuotedEntity(SQLEntity):
    quote = '`'

class SQLColumn(SQLQuotedEntity):
    """
        SQLColumn: represents a column in a table
    """
    def __init__(self, column_name, column_table = False, column_alias=False):
        if not column_table:
            name = '{0}{1}{0}'.format(self.quote, column_name)
        else:
            name = '{0}{1}{0}.{0}{2}{0}'.format(self.quote, column_table, column_name)

        if column_alias:
            self._value = '{0} AS {1}'.format(name, column_alias)
        else:
            self._value = name

    def __unicode__(self):
        return self._value

class SQLTable(SQLQuotedEntity): 
    """
        SQLColumn: represents a table in a database
    """
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