# -*- coding: utf-8 -*-
"""
    fysql.columns
    ~~~~~~~~~~~~~
    :copyright: (c) 2016 by Gasquez Florian
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
from .entities import SQLColumn

class Column(object):
    """
        Column: Python class who represents a SQL column.
    """
    def __init__(self, pkey=False, unique=False, index=False, null=False, default=False, sql_column=False, description=False):
        self.pkey        = pkey
        self.unique      = unique
        self.index       = index
        self.null        = null
        self.default     = default
        self.sql_column  = sql_column
        self.description = description
        self._data       = None

    def bind(self, table, name):
        self.table  = table
        self.name   = name
        self.sql_column   = self.sql_column if self.sql_column else self.name
        self.sql_entities = { # SQL Entity for Column
            'condition': SQLColumn(self.table._name, self.sql_column),
            'selection': SQLColumn(self.table._name, self.sql_column, '{0}_{1}'.format(self.table._name, self.sql_column))
        }

    def _dict(self, value):
        pass

    def _json(self, value):
        pass

class VirtualColumn(object):
    pass

class CharColumn(Column):
    pass

class PKeyColumn(Column):
    def __init__(self, **kwargs):
        kwargs['pkey'] = True
        super(PKeyColumn, self).__init__(**kwargs)

class FKeyColumn(Column):
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

