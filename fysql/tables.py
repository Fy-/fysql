# -*- coding: utf-8 -*-
"""
    fysql.tables
    ~~~~~~~~~~~~
    :copyright: (c) 2016 by Gasquez Florian
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
from collections import OrderedDict

from .columns import Column, PKeyColumn
from .entities import SQLTable
from .containers import SelectContainer
from .exceptions import FysqlException

tables = OrderedDict()

class TableWatcher(type):
    """
        TableWatcher: Watch declaration of subclasses of Table and initialize the data
    """
    def __init__(cls, name, bases, clsdict):
        if len(cls.mro()) > 2 and cls.__name__ != 'Table':
            columns  = []
            db_table = False
            db       = False
            pkey     = False

            # Add fields and static properties
            for key, attr in clsdict.items():
                if isinstance(attr, Column):
                    if attr.pkey == False:
                        columns.append((key, attr))
                    else:
                        pkey = attr
                else:
                    if key == 'db_table':
                        db_table = attr
                    if key == 'db':
                        db = attr

            # Get db in herited
            if bases[0].__name__ != 'Table':
                if bases[0].__dict__.has_key('db'):
                    db = bases[0].__dict__['db']

            if db == False:
                raise FysqlException('No database for {0} ({1})'.format(cls.__name__, cls))

            cls._name       = cls.__name__.lower()
            cls._db_table   = db_table if db_table else cls._name
            cls._sql_entity = SQLTable(cls._db_table)
            cls._columns    = OrderedDict()
            cls._defaults   = OrderedDict()
            cls._backrefs   = OrderedDict()
            cls._foreigns   = []
            cls._database   = db

            # Add a primary key named 'id' if no primary key
            if pkey == False:
                pkey = PKeyColumn()
                columns.insert(0, ('id', pkey))
                setattr(cls, 'id', pkey)

            cls._pkey = pkey

            for key, column in columns:
                column.bind(cls, key) # bind each column to the table.
                cls._add_column(key, column) # save column to table class.

                if column.default:
                    cls._set_default(key, column.default) # save default value

            # add table to tables.
            if tables.has_key(cls._name):
                del tables[cls._name]

            tables[cls._name] = cls

        super(TableWatcher, cls).__init__(name, bases, clsdict)

class Table(object):
    """
        Table: Python class who represents a SQL table
    """
    __metaclass__ = TableWatcher

    @classmethod
    def select(cls):
        return SelectContainer(cls) 

    @classmethod
    def where(cls, *conditions):
        return SelectContainer(cls).where(*conditions)

    # Helpers
    @classmethod
    def _add_column(cls, key, column):
        cls._del_column(key)
        cls._columns[key] = column

    @classmethod
    def _del_column(cls, key):
        if key in cls._columns:
            del cls._columns[key]

    @classmethod
    def _set_default(cls, key, value):
        cls._defaults[key] = value

    @classmethod
    def _add_foreign(cls, table, left_on, right_on):
        cls._foreigns.append({'table': table, 'left_on':unicode(left_on), 'right_on':unicode(right_on)})