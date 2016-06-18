# -*- coding: utf-8 -*-
"""
    fysql.columns
    ~~~~~~~~~~~~~
    :copyright: (c) 2016 by Gasquez Florian
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
from .entities import SQLColumn, SQLCondition
from .exceptions import FysqlException

class Column(object):
    """
        Column: Python class who represents a SQL column.
    """
    column = True

    def __init__(self, pkey=False, unique=False, index=False, null=False, default=False, sql_column=False, description=False):
        self.pkey         = pkey
        self.unique       = unique
        self.index        = index
        self.null         = null
        self.default      = default
        self.sql_column   = sql_column
        self.description  = description
        self._data        = None
        self.sql_entities = False

    def bind(self, table, name):
        self.table  = table
        self.name   = name
        self.sql_column   = self.sql_column if self.sql_column else self.name
        self.sql_entities = { # SQL entities for Column
            'condition': SQLColumn(self.table._name, self.sql_column),
            'selection': SQLColumn(self.table._name, self.sql_column, '{0}_{1}'.format(self.table._name, self.sql_column))
        }

    def _dict(self, value):
        pass

    def _json(self, value):
        pass

    def escape(self, value):
        if isinstance(value, list):
            return map(self._escape, value)
        else:
            return self._escape(unicode(value))


    def _condition(operator):
        """
            Lightweight factory which returns a method that builds an SQLCondition
            from peewee: https://github.com/coleifer/peewee/blob/master/peewee.py#L508-L517
        """
        def inner(self, other):
            if other is None and operator == '=':
                return SQLCondition(self, 'IS', 'null')
            elif other is None and operator == '!=':
                return SQLCondition(self, 'IS NOT', 'null')

            return SQLCondition(self, operator, other)
        return inner

    __eq__      = _condition('=')
    __ne__      = _condition('!=')
    __lt__      = _condition('<')
    __le__      = _condition('<=')
    __gt__      = _condition('>')
    __ge__      = _condition('>=')
    __lshift__  = _condition('IN')
    __mod__     = _condition('LIKE') 

    def __rand__(self, other):
        raise FysqlException('Please use parenthesis: (Table.column_1 == 1) & (Table.column_2 == 2)')

    def __ror__(self, other):
        raise FysqlException('Please use parenthesis: (Table.column_1 == 1) | (Table.column_2 == 2)')

    def __invert__(self):
        raise FysqlException('Please use parenthesis: ~(Table.column_1 == 1)')

    def contains(self, other):
        return SQLCondition(self, 'LIKE', '%%s%%' % other)

    def startswith(self, other):
        return SQLCondition(self, 'LIKE', '%s%%' % other)

    def endswith(self, other):
        return SQLCondition(self, 'LIKE', '%%s' % other)

    def __unicode__(self):
        if self.sql_entities:
            return unicode(self.sql_entities['condition'])
        else:
            return unicode(self.__str__())

class VirtualColumn(object):pass

class CharColumn(Column):
    def _escape(self, value):
        # @todo: to_unicode, escape_string
        value = value
        return '\'{0}\''.format(value)

class IntegerColumn(Column):
    def _escape(self, value):
        return unicode(int(value))

class BigIntegerColumn(IntegerColumn): pass


class PKeyColumn(BigIntegerColumn):
    def __init__(self, **kwargs):
        kwargs['pkey'] = True
        super(PKeyColumn, self).__init__(**kwargs)

class FKeyColumn(BigIntegerColumn):
    def __init__(self, table, reference, link=False, **kwargs):
        self.reference = reference
        self.relation_table = table
        self.link = link if link else self.relation_table._columns['id']
        super(FKeyColumn, self).__init__(**kwargs)

    def bind(self, table, name):
        super(FKeyColumn, self).bind(table, name)
        
        # add foreign column in table
        self.table._add_foreign(self.relation_table, self.sql_entities['condition'], self.link.sql_entities['condition'])

        # add a virtual column for results
        setattr(self.table, self.reference, VirtualColumn())

