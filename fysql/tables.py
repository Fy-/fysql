# -*- coding: utf-8 -*-
"""
    fysql.tables
    ~~~~~~~~~~~~
    :copyright: (c) 2016 by Gasquez Florian
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
from collections import OrderedDict
import json

from .databases import Database
from .columns import Column, PKeyColumn, FKeyColumn
from .entities import SQLTable
from .containers import SelectContainer, CreateContainer, DropContainer, InsertContainer, SaveContainer, RemoveContainer
from .exceptions import FysqlException

class TableWatcher(type):
    """Watch declaration of subclasses of Table and initialize the data"""
    def __init__(cls, name, bases, clsdict):
        if len(cls.mro()) > 2 and cls.__name__ != 'Table':
            columns  = []
            db_table = False
            db       = False
            pkey     = False
            virtual  = True

            # Add fields and static properties
            for key, attr in clsdict.items():
                if isinstance(attr, Column):
                    if attr.pkey == False:
                        columns.append((key, attr))
                        virtual = False
                    else:
                        pkey = attr
                else:
                    if key == 'db_table':
                        db_table = attr
                    if key == 'db':
                        db = attr

            # Get db if herited
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
            cls._for_tables = OrderedDict()
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

            # add table to database.
            if isinstance(cls._database, Database) and not virtual:
                if cls._database._tables.has_key(cls._name):
                    del cls._database._tables[cls._name]

                cls._database._tables[cls._name] = cls

        super(TableWatcher, cls).__init__(name, bases, clsdict)

class Table(object):
    """Python class who represents a SQL table"""
    __metaclass__ = TableWatcher

    def __init__(self):
        self._data = OrderedDict()

    def remove(self):
        return RemoveContainer(self.__class__, self)

    def save(self):
        return SaveContainer(self.__class__, self)

    @classmethod
    def count(cls):
        return SelectContainer(cls, count=True)

    @classmethod
    def count_all(cls):
        return SelectContainer(cls, count=True).execute()

    @classmethod
    def select(cls):
        return SelectContainer(cls) 

    @classmethod
    def where(cls, *conditions):
        return SelectContainer(cls).where(*conditions)

    @classmethod
    def limit(cls, limit, position=0):
        return SelectContainer(cls).limit(limit, position)

    @classmethod
    def get(cls, *conditions):
        try:
            return SelectContainer(cls).where(*conditions).limit(1).execute()[0]
        except IndexError:
            return False

    @classmethod
    def create(cls, **kwargs):
        return InsertContainer(cls, **kwargs).execute()

    @classmethod
    def create_table(cls):
        return CreateContainer(cls)

    @classmethod
    def drop_table(cls):
        return DropContainer(cls)


    @classmethod
    def _add_column(cls, key, column):
        cls._columns[key] = column

    @classmethod
    def _set_default(cls, key, value):
        cls._defaults[key] = value

    @classmethod
    def _add_foreign(cls, table, left_on, right_on):
        cls._foreigns.append({'table': table, 'left_on':unicode(left_on), 'right_on':unicode(right_on)})
        cls._for_tables[table._db_table] = table


    def _dict(self):
        d = OrderedDict()
        for key, column in self._columns.items():
            d[key] = column._dict(getattr(self, key))
            if isinstance(column, FKeyColumn):
                d[column.reference] = getattr(self, column.reference)._dict()

        return d

    def _json(self, indent=None):
        return json.dumps(self._dict(), indent=indent, sort_keys=False)

    def __str__(self):
        return self._json(indent=2)
        
    def __repr__(self):
        return self._json()
