# -*- coding: utf-8 -*-
"""
    fysql.containers
    ~~~~~~~~~~~~~~~~
    :copyright: (c) 2016 by Gasquez Florian
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
import hashlib

from .entities import SQLEntity, SQLJoin, SQLCondition
from .columns import FKeyColumn, PKeyColumn

class ContainerWalker(object):
    """
        ContainerWalker: walk through a list of SQLEntity and EntityContainer
        Convert this list to a sql query --> self.sql
    """
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if not args[2]:
            return super(ContainerWalker, cls).__new__(cls, *args, **kwargs)

        key = hashlib.md5(str(args[0])).hexdigest()
        if not ContainerWalker._instances.has_key(key):
            ContainerWalker._instances[key] = super(ContainerWalker, cls).__new__(cls, *args, **kwargs)
        return ContainerWalker._instances[key]

    def __init__(self, entities, separator, executable, *args, **kwargs):
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

class ResultContainer(object):
    """
        Assign sql select datas to Table._data
    """
    def __init__(self, table, cursor):
        self.table  = table
        self.cursor = cursor
        self.sql2py = {}
        self.result = []

        for i in range(len(self.cursor.description)):
           self.sql2py[i] = self.cursor.description[i][0]

        self.parse()

    def parse(self):
        # @todo: allow fetchone (memory issue?)
        rows = self.cursor.fetchall()
        for row in rows:
            self.parse_row(row)

        self.cursor.close()

    def parse_row(self, row):
        item = self.table()

        for k, f in self.sql2py.items():
            item._data[f] = row[k]

        self.result.append(item)

class EntityContainer(object):
    """
        self.entities -> List of SQLEntity and Entity containers
    """
    def __new__(cls, *args, **kwargs):
        if args:
            cls.executable = True
        else:
            cls.executable = False

        return super(EntityContainer, cls).__new__(cls, *args, **kwargs)

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
            self._walker = ContainerWalker(self.entities, self.separator, self.executable)
        return self._walker

class EntityExecutableContainer(EntityContainer):
    """
        self.entities -> list of SQLEntity and Entity containers
        This list can be converted to an SQL query using ContainerWalker
    """

    """
    _instances = {}

    def __new__(cls, *args, **kwargs):
        key = cls.__name__ + args[0].__name__
        if not cls._instances.has_key(key):
            EntityExecutableContainer._instances[key] = super(EntityExecutableContainer, cls).__new__(cls, *args, **kwargs)
        return EntityExecutableContainer._instances[key]
    """

    def __init__(self, table):
        super(EntityExecutableContainer, self).__init__()
        self.table = table

    @property
    def sql(self):
        return self.walker.sql

    def execute(self, commit=False):
        if isinstance(self.table._database, str):
            return False
        return self.table._database.execute(self.sql, commit=commit)
    

class DropContainer(EntityExecutableContainer):
    """
       self.entities -> list representing a DROP query
    """
    def __init__(self, table):
        super(DropContainer, self).__init__(table)
        self += SQLEntity('DROP TABLE IF EXISTS {0};'.format(self.table._sql_entity))
        self.execute()


class CreateContainer(EntityExecutableContainer):
    """
        self.entities -> list representing a CREATE query
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

            if column.pkey:
                column_create += SQLEntity('AUTO_INCREMENT')

            args_create += column_create

            if column.index:
                unique = '' if not column.unique else 'UNIQUE'
                indexes += SQLEntity('{0} INDEX {1} ({2})'.format(unique, column.sql_entities['index'], column.sql_entities['name']))

        args_create += indexes

        self += args_create

        self += SQLEntity(') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;')

        DropContainer(self.table)
        self.execute()

class InsertContainer(EntityExecutableContainer):
    """
        self.entities -> list representing an Insert query
    """
    def __init__(self, table, **kwargs):
        super(InsertContainer, self).__init__(table)
        self += SQLEntity('INSERT INTO')
        self += self.table._sql_entity
        self += SQLEntity('(')

        columns_names  = EntityContainer(separator=',')
        columns_values = EntityContainer(separator=',') 
        for attr, value in kwargs.items():
            if self.table._columns.has_key(attr):
                columns_names  += self.table._columns[attr].sql_entities['name']
                columns_values += self.table._columns[attr].escape(value)

        self += columns_names
        self += SQLEntity(')')
        self += SQLEntity('VALUES (')
        self += columns_values
        self += SQLEntity(');')


    def execute(self):
        cursor  = self.table._database.execute(self.sql)
        item_id = self.table._database.connection.insert_id()
        self.table._database.commit()

        return self.table.get(self.table.id==item_id)

class SaveContainer(EntityExecutableContainer):
    """
        self.entities -> list representing an Insert query
    """
    def __init__(self, table, instance):
        super(SaveContainer, self).__init__(table)
        self += SQLEntity('UPDATE')
        self += self.table._sql_entity
        self += SQLEntity('SET')

        columns = EntityContainer(separator=',')
        to_update = []
        for key, column in self.table._columns.items():
            columns += SQLEntity('{0}={1}'.format(
                column, 
                column.escape(getattr(instance, key))
                )
            )
            if isinstance(column, FKeyColumn):
                to_update.append(getattr(instance, column.reference))



        self += columns
        self += SQLEntity('WHERE {0}={1} LIMIT 1'.format(
            self.table._pkey, 
            getattr(instance, self.table._pkey.name)
        ))
        self.execute(commit=True)

        for item in to_update:
            item.save()

class RemoveContainer(EntityExecutableContainer):
    """
        self.entities -> list representing an Insert query
    """   
    def __init__(self, table, instance):
        super(RemoveContainer, self).__init__(table)
        self += SQLEntity('DELETE FROM')
        self += self.table._sql_entity
        self += SQLEntity('WHERE {0}={1} LIMIT 1'.format(
            self.table._pkey, 
            getattr(instance, self.table._pkey.name)
        ))

        self.execute(commit=True)



class ConditionableExecutableContainer(EntityExecutableContainer):
    """
        Conditionable query, with where, limit, group, having...
    """   
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

class SelectContainer(ConditionableExecutableContainer):
    """
        self.entities -> list representing a SELECT query
    """
    def __init__(self, table, count=False):
        super(SelectContainer, self).__init__(table)
        self.count = count

        # add selected columns
        columns = EntityContainer(separator=',')
        for key, column in self.table._columns.items():
            columns += column.sql_entities['selection']

        # add selected tables
        tables = EntityContainer(separator=',')
        tables += self.table._sql_entity
        
        # add joins
        joins    = EntityContainer()
        for foreign in self.table._foreigns:
            joins += SQLJoin('INNER', foreign['table']._sql_entity, foreign['left_on'], foreign['right_on'])
            for key, column in foreign['table']._columns.items():
                columns += column.sql_entities['selection']

        self += SQLEntity('SELECT')
        if self.count:
            self += SQLEntity('COUNT(*)')
        else:
            self += columns
        self += SQLEntity('FROM')
        self += tables
        
        if len(joins) != 0:
            self += joins

    def execute(self):
        cursor = self.table._database.execute(self.sql)

        if self.count:
            return cursor.fetchone()[0]

        return ResultContainer(self.table, cursor).result

    @property
    def result(self):
        return self.execute()
    