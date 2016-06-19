# -*- coding: utf-8 -*-
"""
    fysql.columns
    ~~~~~~~~~~~~~
    :copyright: (c) 2016 by Gasquez Florian
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
import json

from .entities import SQLColumn, SQLCondition, SQLQuotedEntity
from .exceptions import FysqlException

class Column(object):
    """
        Column: epresents a SQL column on a Table.
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
        self.sql_entities = False

    def __get__(self, instance, type=None):
        if instance is not None:
            return instance._data.get('{0}_{1}'.format(self.table._db_table, self.name))
        return self

    def __set__(self, instance, value):
        instance._data['{0}_{1}'.format(self.table._db_table, self.name)] = value

    def bind(self, table, name):
        self.table  = table
        self.name   = name
        self.sql_column   = self.sql_column if self.sql_column else self.name
        self.sql_entities = { # SQL entities for Column
            'name'     : SQLColumn(self.sql_column),
            'condition': SQLColumn(self.sql_column, self.table._db_table),
            'selection': SQLColumn(self.sql_column, self.table._db_table, '{0}_{1}'.format(self.table._db_table, self.sql_column))
        }
        if self.index:
            self.sql_entities['index'] = SQLQuotedEntity('{0}_index'.format(self.sql_column))

    def _json(self, value):
        return json.dumps(self._dict(value))

    def _dict(self, value):
        return value

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

class VirtualColumn(object):
    """
        Represents an other Table as a Column
    """
    def __init__(self, table, name):
        self.table    = table
        self.name     = name

    def __get__(self, instance, type=None):
        if instance is not None:
            key = '{0}_{1}'.format(self.table._db_table, self.name)
            if not instance._data.get(key):
                instance._data[key] = self.table()
                for k, data in instance._data.items():
                    if self.name == k.split('_')[0] and key != k:
                        instance._data[key]._data[k] = data
                        del instance._data[k]

                return instance._data[key]
            else:
                return instance._data.get(key)
        return self

    def __set__(self, instance, value):
        key = '{0}_{1}'.format(self.table._db_table, self.name)
        instance._data[key] = value

class CharColumn(Column):
    sql_type = 'varchar'

    def __init__(self, max_length=255, **kwargs):
        super(CharColumn, self).__init__(**kwargs)

        self.sql_type_size = max_length

        if self.index and max_length > 190:
            self.sql_type_size = 190
        

    def _escape(self, value):
        # @todo: to_unicode, escape_string
        value = value
        return '\'{0}\''.format(value)

class IntegerColumn(Column):
    sql_type = 'int'
    sql_type_size = 11

    def _escape(self, value):
        return unicode(int(value))

class TinyIntegerColumn(IntegerColumn):
    sql_type = 'tinyint'
    sql_type_size = 4

class SmallIntegerColumn(IntegerColumn):
    sql_type = 'smallint'
    sql_type_size = 6

class BigIntegerColumn(IntegerColumn):
    sql_type = 'bigint'
    sql_type_size = 20

class PKeyColumn(BigIntegerColumn):
    def __init__(self, **kwargs):
        kwargs['pkey'] = True
        super(PKeyColumn, self).__init__(**kwargs)

class FKeyColumn(BigIntegerColumn):
    def __init__(self, table, reference, link=False, **kwargs):
        kwargs['index'] = True
        self.reference = reference
        self.relation_table = table
        self.link = link if link else self.relation_table._columns['id']

        super(FKeyColumn, self).__init__(**kwargs)

    def bind(self, table, name):
        super(FKeyColumn, self).bind(table, name)
        
        # add foreign column in table
        self.table._add_foreign(self.relation_table, self.sql_entities['condition'], self.link.sql_entities['condition'])

        # add a virtual column for results
        setattr(self.table, self.reference, VirtualColumn(self.relation_table, self.reference)) # @todo: alias to external columns with alias = reference

