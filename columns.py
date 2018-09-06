# -*- coding: utf-8 -*-
"""
    fysql.columns
    ~~~~~~~~~~~~~
    :copyright: (c) 2016 by Gasquez Florian
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
import json
import _pickle as cPickle

from .entities import SQLColumn, SQLCondition, SQLQuotedEntity
from .exceptions import FysqlException
from .utils import format_date_time


class Column(object):
    """Represents a SQL column on a Table."""
    quoted = False
    sql_type = None
    sql_type_size = None

    def __init__(
        self, pkey=False, unique=False, index=False, null=False,
        default=False, sql_column=False, description=False,
        setter=False, getter=False
    ):
        self.pkey = pkey
        self.unique = unique
        self.index = index
        self.null = null
        self.default = default
        self.sql_column = sql_column
        self.description = description
        self.sql_entities = False
        self.setter = setter
        self.getter = getter
        self.filled = False

    def __get__(self, instance, type=None):
        if instance is not None:
            return instance._data.get('{0}_{1}'.format(self.table._db_table, self.name))
        return self

    def __set__(self, instance, value):
        if self.setter:
            value = self.setter(value)
        self.filled = True
        instance._data['{0}_{1}'.format(self.table._db_table, self.name)] = value

    def bind(self, table, name):
        self.table = table
        self.name = name
        self.sql_column = self.sql_column if self.sql_column else self.name
        self.sql_entities = {  # SQL entities for Column
            'name': SQLColumn(self.sql_column),
            'condition': SQLColumn(self.sql_column, self.table._db_table),
            'selection': SQLColumn(self.sql_column, self.table._db_table, '{0}_{1}'.format(self.table._db_table, self.sql_column)),
        }
        if self.index:
            self.sql_entities['index'] = SQLQuotedEntity('{0}_index'.format(self.sql_column))

    def _json(self, value):
        return self.escape(value, no_quote=True)

    def escape(self, value, no_quote=False):
        if isinstance(value, list):
            values = map(self._escape, value)
            if self.quoted:
                for value in values:
                    value = '\'{0}\''.format(self.table._database.escape_string(value))

            return values
        else:
            if hasattr(value, '__call__'):
                value = value()

            if self.quoted and not isinstance(value, Column) and no_quote is False:
                return '\'{0}\''.format(self.table._database.escape_string(self._escape(value)))

            return self._escape(value)

    def _condition(operator):
        """Lightweight factory which returns a method that builds an SQLCondition.
        From peewee:
            https://github.com/coleifer/peewee/blob/master/peewee.py#L508-L517
        """

        def inner(self, other):
            if other is None and operator == '=':
                return SQLCondition(self, 'IS', 'null')
            elif other is None and operator == '!=':
                return SQLCondition(self, 'IS NOT', 'null')

            return SQLCondition(self, operator, other)
        return inner

    __eq__ = _condition('=')
    __ne__ = _condition('!=')
    __lt__ = _condition('<')
    __le__ = _condition('<=')
    __gt__ = _condition('>')
    __ge__ = _condition('>=')
    __lshift__ = _condition('IN')
    __mod__ = _condition('LIKE')

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

    def __str__(self):
        if self.sql_entities:
            return str(self.sql_entities['condition'])
        else:
            return str(self.__str__())

    def __hash__(self):
        return hash('{0}_{1}'.format(self.table._name, self.sql_column))


class VirtualColumn(object):
    """Represents an other Table as a Column"""

    def __init__(self, table, relation_table, name):
        self.table = table
        self.relation_table = relation_table
        self.name = name

    def __get__(self, instance, type=None):
        if instance is not None:
            key = '{0}_{1}'.format(self.table._db_table, self.name)
            if not instance._data.get(key):
                instance._data[key] = self.relation_table()
                temp = instance._data.copy()
                for k, data in temp.items():
                    if self.name == k.split('_')[0] and key != k:
                        tk = k
                        k = k.split('_')
                        k[0] = self.table._backrefs[self.name]
                        k = '_'.join(k)

                        instance._data[key]._data[k] = data
                        del instance._data[tk]

                if not getattr(instance._data[key], instance._pkey_name):
                    return False

                instance.__load__()
                return instance._data[key]
            else:
                return instance._data.get(key)
        return self

    """
    def __set__(self, instance, value):
        key = '{0}_{1}'.format(self.table._db_table, self.name)
        instance._data[key] = value
    """

    def _dict(self):
        return False


class CharColumn(Column):
    sql_type = 'varchar'
    quoted = True

    def __init__(self, max_length=255, **kwargs):
        super(CharColumn, self).__init__(**kwargs)

        self.sql_type_size = max_length

        if self.index and max_length > 190:
            self.sql_type_size = 190

    def _escape(self, value):
        # @todo: to_unicode, escape_string
        value = value
        return value


class TextColumn(Column):
    sql_type = 'text'
    quoted = True

    def _escape(self, value):
        # @todo: to_unicode, escape_string
        value = value
        return value


class DictColumn(TextColumn):

    def _escape(self, value):
        if value is None:
            #return cPickle.dumps({})
            json.dumps({})
        return json.dumps(value)

    def _py(self, value):
        if value:
            return json.loads(str(value))
        else:
            return {}

    def _json(self, value):
        try:
            return json.dumps(value)
        except:
            return 'DictColumn: not JSON serializable'


class IntegerColumn(Column):
    sql_type = 'int'
    sql_type_size = 11

    def _escape(self, value):
        return int(value or 0)


class FloatColumn(Column):
    sql_type = 'float'

    def _escape(self, value):
        return float(value or 0.)


class TinyIntegerColumn(IntegerColumn):
    sql_type = 'tinyint'
    sql_type_size = 4


class BooleanColumn(TinyIntegerColumn):
    db_size = 1


class SmallIntegerColumn(IntegerColumn):
    sql_type = 'smallint'
    sql_type_size = 6


class BigIntegerColumn(IntegerColumn):
    sql_type = 'bigint'
    sql_type_size = 20


class DateTimeColumn(Column):
    sql_type = 'datetime'
    sql_format = '%Y-%m-%d %H:%M:%S'
    quoted = True

    def __init__(self, sql_format=None, **kwargs):
        super(DateTimeColumn, self).__init__(**kwargs)
        self.sql_format = sql_format if sql_format else self.sql_format

    def _escape(self, value):
        return format_date_time(value, self.sql_format)

    def _json(self, value):
        return format_date_time(value, self.sql_format)


class DateColumn(DateTimeColumn):
    sql_type = 'date'
    sql_format = '%Y-%m-%d'


class TimeColumn(DateTimeColumn):
    sql_type = 'time'
    sql_format = '%H:%M:%S'


class PKeyColumn(BigIntegerColumn):

    def __init__(self, **kwargs):
        kwargs['pkey'] = True
        super(PKeyColumn, self).__init__(**kwargs)


class FKeyColumn(BigIntegerColumn):

    def __init__(self, table, reference, link=False, required=True, **kwargs):
        kwargs['index'] = True
        self.reference = reference
        self.required = required
        self.relation_table = table
        self.link = link if link else self.relation_table._columns['id']

        super(FKeyColumn, self).__init__(**kwargs)

    def bind(self, table, name):
        super(FKeyColumn, self).bind(table, name)

        # add foreign column in table
        self.table._add_foreign(self)

        # add a virtual column for results
        vc = VirtualColumn(self.table, self.relation_table, self.reference)
        setattr(self.table, self.reference, vc)  # @todo: alias to external columns with alias = reference
