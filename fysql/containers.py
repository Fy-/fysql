# -*- coding: utf-8 -*-
"""
    fysql.containers
    ~~~~~~~~~~~~~~~~
    :copyright: (c) 2016 by Gasquez Florian
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
from .entities import SQLEntity

class ContainerWalker(object):
    """
        ContainerWalker: walk through a list of SQLEntity and EntityContainer
        Convert this list to a sql query. (self.sql)
    """
    def __init__(self, entities, separator, *args, **kwargs):
        self._sql = False
        self.entities  = entities
        self.separator = separator

    def prepare(self):
        sql = []
        for entity in self.entities:
            if isinstance(entity, EntityContainer):
                sql.append(
                    entity.separator.join(
                        map(unicode, entity.walker.prepare())
                    )
                )
            else:
                sql.append(unicode(entity))

        self._sql = self.separator.join(map(unicode, sql))

        return sql

    @property
    def sql(self):
        if self._sql == False:
            self.prepare()
        return self._sql

    @staticmethod
    def _sql_entity(value):
        return '{0}{1}'.format(unicode(value))

class EntityContainer(object):
    """
        Contain a list of SQLEntity and Entity containers
    """
    def __init__(self, separator=' '):
        self._walker    = False
        self.entities   = []
        self.separator  = separator

    def add(self, entity):
        self.entities.append(entity) 

    @property
    def walker(self):
        if not self._walker:
            self._walker = ContainerWalker(entities=self.entities, separator=self.separator)
        return self._walker

    @property
    def sql(self):
        return self.walker.sql

class SelectContainer(EntityContainer):
    """
        Contain a list representing a SELECT query
    """
    def __init__(self, table):
        super(SelectContainer, self).__init__()
        self.table = table

        self.add(SQLEntity('SELECT'))

        columns = EntityContainer(separator=',')
        for key, column in self.table._columns.items():
            columns.add(column.sql_entities['select'])

        self.add(columns)
        self.add(SQLEntity('FROM'))
        self.add(table._sql_entity)