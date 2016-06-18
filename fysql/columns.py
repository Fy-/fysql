# -*- coding: utf-8 -*-
"""
    fysql.columns
    ~~~~~~~~~~~~~
    :copyright: (c) 2016 by Gasquez Florian
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
from collections import OrderedDict

from .entities import *

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

    def bind(self, table, name):
        self.table  = table
        self.name   = name
        self.sql_column   = self.sql_column if self.sql_column else self.name
        self.sql_entities = { # SQL Entity for Column
            'select' : SQLColumn(self.table._name, self.sql_column) 
        }

    def _dict(self, value):
        pass

    def _json(self, value):
        pass

class CharColumn(Column):
    pass

class PKeyColumn(Column):
    def __init__(self, **kwargs):
        kwargs['pkey'] = True
        super(PKeyColumn, self).__init__(**kwargs)
