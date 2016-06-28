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
from .containers import SelectContainer, CreateContainer, DropContainer, InsertContainer, SaveContainer, RemoveContainer, CreateTableContainer
from .exceptions import FysqlException


class TableWatcher(type):
    """Watch declaration of subclasses of Table and initialize the data"""
    def __init__(cls, name, bases, clsdict):
        if len(cls.mro()) > 2 and cls.__name__ != 'Table':
            columns = []
            db_table = False
            db = False
            pkey = False
            virtual = True

            # Add fields and static properties
            for key, attr in clsdict.items():
                if isinstance(attr, Column):
                    columns.append((key, attr))
                    if attr.pkey is True:
                        pkey = True
                        cls._pkey = attr
                        cls._pkey_name = key

                    virtual = False
                else:
                    if key == 'db_table':
                        db_table = attr
                    if key == 'db':
                        db = attr

            # Get db if herited
            if bases[0].__name__ != 'Table':
                if 'db' in bases[0].__dict__.keys():
                    db = bases[0].__dict__['db']

            if db is False:
                raise FysqlException('No database for {0} ({1})'.format(cls.__name__, cls))

            cls._name = cls.__name__.lower()
            cls._db_table = db_table if db_table else cls._name
            cls._sql_entity = SQLTable(cls._db_table)
            cls._columns = OrderedDict()
            cls._defaults = OrderedDict()
            cls._backrefs = OrderedDict()
            cls._for_tables = OrderedDict()
            cls._foreigns = []
            cls._database = db

            # Add a primary key named 'id' if no primary key
            if not pkey:
                pkey = PKeyColumn()
                columns.insert(0, ('id', pkey))
                setattr(cls, 'id', pkey)
                cls._pkey = pkey
                cls._pkey_name = 'id'

            for key, column in columns:
                column.bind(cls, key)  # bind each column to the table.
                cls._add_column(key, column)  # save column to table class.

                if column.default:
                    cls._set_default(key, column.default)  # save default value

            # add table to database.
            if isinstance(cls._database, Database) and not virtual:
                if cls._name in cls._database._tables.keys():
                    del cls._database._tables[cls._name]

                cls._database._tables[cls._name] = cls

        super(TableWatcher, cls).__init__(name, bases, clsdict)


class Table(object):
    """Python class who represents a SQL table"""
    __metaclass__ = TableWatcher

    def __init__(self):
        self._data = OrderedDict()

    def __load__(self):
        pass

    def remove(self):
        return RemoveContainer(self.__class__, self)

    def save(self):
        return SaveContainer(self.__class__, self)

    def insert(self):
        return InsertContainer(self.__class__, self).execute()

    @classmethod
    def count_filter(cls, *conditions):
        return SelectContainer(cls, is_count=True).where(*conditions).all()

    @classmethod
    def count(cls):
        return SelectContainer(cls, is_count=True).execute()

    @classmethod
    def select(cls, *args, **kwargs):
        return SelectContainer(cls, *args, **kwargs)

    @classmethod
    def all(cls):
        return SelectContainer(cls).all()

    @classmethod
    def filter(cls, *conditions):
        return SelectContainer(cls).where(*conditions)

    @classmethod
    def limit(cls, limit, position=0):
        return SelectContainer(cls).limit(limit, position)

    @classmethod
    def get(cls, *conditions):
        return SelectContainer(cls).where(*conditions).one()

    @classmethod
    def create(cls, **kwargs):
        return CreateContainer(cls, **kwargs).execute()

    @classmethod
    def create_table(cls):
        return CreateTableContainer(cls)

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
    def _add_foreign(cls, column):
        cls._foreigns.append({
            'table': column.relation_table,
            'column': column,
            'left_on': unicode(column.sql_entities['condition']),
            'right_on': unicode(column.link.sql_entities['condition'])
        })
        cls._for_tables[column.relation_table._db_table] = column.relation_table
        cls._backrefs[column.reference] = column.relation_table._db_table

    def _dict(self):
        d = OrderedDict()
        for key, column in self._columns.items():
            d[key] = getattr(self, key)
            if isinstance(column, FKeyColumn):
                d[column.reference] = getattr(self, column.reference)

        return d

    def _json(self, indent=None):
        d = OrderedDict()
        for key, column in self._columns.items():
            d[key] = column._json(getattr(self, key))
            if isinstance(column, FKeyColumn):
                v = getattr(self, column.reference)
                if v:
                    d[column.reference] = getattr(self, column.reference)._json()
                else:
                    d[column.reference] = False

        return json.dumps(d, indent=indent, sort_keys=False)

    def __repr__(self):
        return '<%s %s:%s>' % (self.__class__.__name__, self._pkey_name, getattr(self, self._pkey_name))
