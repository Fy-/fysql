# -*- coding: utf-8 -*-
"""
    fysql.containers
    ~~~~~~~~~~~~~~~~
    :copyright: (c) 2016 by Gasquez Florian
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
from .entities import SQLEntity, SQLJoin, SQLCondition
from .columns import FKeyColumn, PKeyColumn

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

        self._sql = self.separator.join(map(unicode, sql)).strip()

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

    def __add__(self, entity):
        self.entities.append(entity) 
        return self

    def __len__(self):
        return len(self.entities)

    @property
    def walker(self):
        if not self._walker:
            self._walker = ContainerWalker(self.entities, self.separator)
        return self._walker

    @property
    def sql(self):
        return self.walker.sql

class EntityExecutableContainer(EntityContainer):
    def __init__(self, table):
        super(EntityExecutableContainer, self).__init__()
        self.table = table

class DropContainer(EntityExecutableContainer):
    """
        Contain a list representing a DROP query
    """
    def __init__(self, table):
        super(DropContainer, self).__init__(table)
        self += SQLEntity('DROP TABLE IF EXISTS {0};'.format(self.table._sql_entity))


class CreateContainer(EntityExecutableContainer):
    """
        Contain a list representing a CREATE query
    """
    def __init__(self, table):
        super(CreateContainer, self).__init__(table)

        self += SQLEntity('CREATE TABLE IF NOT EXISTS {0} ('.format(self.table._sql_entity))
        
        args_create = EntityContainer(separator=', ')
        indexes     = EntityContainer(separator=', ')

        indexes += SQLEntity('PRIMARY KEY ({0})'.format(self.table._pkey.sql_entities['name']))

        for key, column in self.table._columns.items():
            column_create = EntityContainer(separator=' ')
            column_create += column.sql_entities['name']
            
            if column.sql_type_size:
                column_create += SQLEntity('{0}({1})'.format(column.sql_type, column.sql_type_size))
            else:
                column_create += SQLEntity(column.sql_type)

            if isinstance(column, FKeyColumn) or isinstance(column, PKeyColumn):
                column_create += SQLEntity('UNSIGNED')

            if column.unique and not column.index:
                column_create += SQLEntity('UNIQUE')

            if column.null == False:
                column_create += SQLEntity('NOT NULL')
            else:
                column_create += SQLEntity('NULL')

            if column.default:
                column_create += SQLEntity('DEFAULT {0}'.format(column.escape(column.default)))

            args_create += column_create

            if column.index:
                unique = '' if not column.unique else 'UNIQUE'
                indexes += SQLEntity('{0} INDEX {1} ({2})'.format(unique, column.sql_entities['index'], column.sql_entities['name']))

        args_create += indexes

        self += args_create

        self += SQLEntity(') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;')

class SelectContainer(EntityExecutableContainer):
    """
        Contain a list representing a SELECT query
    """
    def __init__(self, table):
        super(SelectContainer, self).__init__(table)

        # add selected columns
        columns = EntityContainer(separator=',')
        for key, column in self.table._columns.items():
            columns += column.sql_entities['selection']

        # add selected tables
        tables = EntityContainer(separator=',')
        tables += table._sql_entity
        
        # add joins
        joins    = EntityContainer()
        for foreign in self.table._foreigns:
            joins += SQLJoin('INNER', foreign['table']._sql_entity, foreign['left_on'], foreign['right_on'])
            for key, column in foreign['table']._columns.items():
                columns += column.sql_entities['selection']

        self += SQLEntity('SELECT')
        self += columns
        self += SQLEntity('FROM')
        self += tables
        
        if len(joins) != 0:
            self += joins

    def where(self, *conditions):
        self += SQLEntity('WHERE')

        size = len(conditions)-1
        i    = 0

        if size == 0:
            self += conditions[0]
        else:
            for condition in conditions:
                if isinstance(condition, SQLCondition):
                    self += SQLEntity('(')
                    self += condition
                    self += SQLEntity(')')

                    if i < size:
                        self += SQLEntity('AND')
                    
                i += 1

        return self

    def limit(self, limit, position=0):
        self += SQLEntity('LIMIT {0},{1}'.format(position, limit))
        return self