# -*- coding: utf-8 -*-
"""
	fysql.containers
	~~~~~~~~~~~~~~~~
	:copyright: (c) 2016 by Gasquez Florian
	:license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
from functools import wraps
import copy
import hashlib

from .entities import SQLEntity, SQLJoin, SQLCondition, SQLColumn
from .columns import FKeyColumn, PKeyColumn, IntegerColumn
from .static import Tables

'''
class ContainerWalkerType(type):
	_instances = {}

	def __new__(cls, *args, **kwargs):
		if not args[2]:
			return super(ContainerWalker, cls).__new__(cls, *args, **kwargs)
		key = hashlib.md5(args[0].encode('utf-8')).hexdigest()
		if key not in ContainerWalkerType._instances.keys():
			ContainerWalkerType._instances[key] = super(ContainerWalker, cls).__new__(cls, *args, **kwargs)
		return ContainerWalkerType._instances[key]
'''

class ContainerWalker(object):
	"""ContainerWalker: walk through a list of SQLEntity and EntityContainer.
	Attributes:
		_sql (str): description of the SQL query filled by the walker.
	"""


	def __init__(self, entities, separator, executable, *args, **kwargs):
		self._sql = False
		self.entities = entities
		self.separator = separator

	def prepare(self):
		sql = []
		for entity in self.entities:
			if isinstance(entity, EntityContainer):
				sql.append(
					entity.separator.join(
						map(str, entity.walker.prepare())
					)
				)
			else:
				sql.append(str(entity))

		self._sql = self.separator.join(map(str, sql)).strip()

		return sql

	@property
	def sql(self):
		if self._sql is False:
			self.prepare()
		return self._sql

	@staticmethod
	def _sql_entity(value):
		return '{0}{1}'.format(str(value))


class ResultContainer(object):
	"""Assign sql select datas to Table._data"""

	def __init__(self, table, cursor):
		self.table = table
		self.cursor = cursor
		self.sql2py = {}
		self.result = []
		if self.cursor.description is not None:
			for i in range(len(self.cursor.description)):
				desc =  self.cursor.description[i][0]
				if isinstance(desc, bytes):
					desc = desc.decode('utf-8')
				self.sql2py[i] = desc

			self.parse()

	def parse(self):
		"""Parse rows
		Todo:
			* Allow cursor.fetchone()? (memory issue)
		"""
		rows = self.cursor.fetchall()

		for row in rows:
			self.parse_row(row)

		self.cursor.close()

	def parse_row(self, row):
		item = self.table()

		for k, f in self.sql2py.items():
			tables = Tables.tables

			id_table = f.split('_')[0]
			id_column = f.split('_', 1)[1]

			if id_table != self.table._db_table:
				id_table = self.table._backrefs[id_table]

			if '_py' in dir(tables[id_table]._columns[id_column]):
				item._data[f] = tables[id_table]._columns[id_column]._py(row[k])
			else:
				item._data[f] = row[k]

		item.__load__()
		self.result.append(item)


class EntityContainer(object):
	"""List of SQLEntity
		Attributes:
			entities (list) SQLEntity and EntityContainer
			seperator (str) Separator for each element of entities
	"""


	def __init__(self, separator=' '):
		self._walker = False
		self.entities = []
		self.separator = separator
		self.executable = False

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
	"""List of SQLEntity that can be converted to an executable SQL query."""

	def __init__(self, table):
		super(EntityExecutableContainer, self).__init__()
		self.table = table
		self.executable = True

	@property
	def sql(self):
		return self.walker.sql

	def execute(self, commit=False):
		return self.table._database.execute(self.sql, commit=commit)


class DropContainer(EntityExecutableContainer):
	"""DROP TABLE SQL query."""

	def __init__(self, table):
		super(DropContainer, self).__init__(table)
		self += SQLEntity('DROP TABLE IF EXISTS {0};'.format(self.table._sql_entity))
		self.execute()


class CreateTableContainer(EntityExecutableContainer):
	"""CREATE TABLE SQL query."""

	def __init__(self, table):
		super(CreateTableContainer, self).__init__(table)

		self += SQLEntity('CREATE TABLE IF NOT EXISTS {0} ('.format(self.table._sql_entity))

		args_create = EntityContainer(separator=', ')
		indexes = EntityContainer(separator=', ')

		indexes += SQLEntity('PRIMARY KEY ({0})'.format(self.table._pkey.sql_entities['name']))

		for key, column in self.table._columns.items():
			column_create = EntityContainer(separator=' ')
			column_create += column.sql_entities['name']

			if column.sql_type_size is not None:
				column_create += SQLEntity('{0}({1})'.format(column.sql_type, column.sql_type_size))
			else:
				column_create += SQLEntity(column.sql_type)

			if isinstance(column, FKeyColumn) or isinstance(column, PKeyColumn):
				column_create += SQLEntity('UNSIGNED')

			if column.unique and not column.index:
				column_create += SQLEntity('UNIQUE')

			if column.null is False:
				column_create += SQLEntity('NOT NULL')
			else:
				column_create += SQLEntity('NULL')

			# if column.default:
			#    column_create += SQLEntity('DEFAULT {0}'.format(column.escape(column.default)))

			if column.pkey and isinstance(column, IntegerColumn):
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
	"""Table.insert(table_instance)"""

	def __init__(self, table, instance):
		super(InsertContainer, self).__init__(table)
		self.filled = []
		self.instance = instance
		self.pkey_id = False

		self += SQLEntity('INSERT INTO')
		self += self.table._sql_entity
		self += SQLEntity('(')

		columns_names = EntityContainer(separator=', ')
		columns_values = EntityContainer(separator=', ')

		for key, column in self.table._columns.items():
			value = getattr(self.instance, key)
			print (key +':'+ value)
			if value:
				if column.pkey is True:
					self.pkey_id = value

				columns_names += column.sql_entities['name']
				columns_values += column.escape(getattr(self.instance, key))

			for k, v in self.table._defaults.items():
				if not value and key == k:
					columns_names += self.table._columns[k].sql_entities['name']
					columns_values += column.escape(v)

		self += columns_names
		self += SQLEntity(')')
		self += SQLEntity('VALUES (')
		self += columns_values
		self += SQLEntity(');')

	def execute(self):
		cursor = self.table._database.execute(self.sql)
		if self.pkey_id is False:
			self.pkey_id = self.table._database.insert_id(cursor)

		self.table._database.commit()
		return self.table.get(self.table._pkey == self.pkey_id)


class CreateContainer(EntityExecutableContainer):
	"""INSERT INTO SQL query. Used for Table.create()"""

	def __init__(self, table, **kwargs):
		super(CreateContainer, self).__init__(table)
		self.filled = []
		self.pkey_id = False

		self += SQLEntity('INSERT INTO')
		self += self.table._sql_entity
		self += SQLEntity('(')

		columns_names = EntityContainer(separator=',')
		columns_values = EntityContainer(separator=',')
		for attr, value in kwargs.items():
			if attr in self.table._columns.keys():
				columns_names += self.table._columns[attr].sql_entities['name']
				columns_values += self.table._columns[attr].escape(value)

				if self.table._columns[attr].pkey is True:
					self.pkey_id = value

				self.filled.append(attr)

		for key, column in self.table._defaults.items():
			if key not in self.filled:
				columns_names += self.table._columns[key].sql_entities['name']
				columns_values += self.table._columns[key].escape(self.table._columns[key].default)

		self += columns_names
		self += SQLEntity(')')
		self += SQLEntity('VALUES (')
		self += columns_values
		self += SQLEntity(');')

	def execute(self):
		cursor = self.table._database.execute(self.sql)
		if self.pkey_id is False:
			self.pkey_id = self.table._database.insert_id(cursor)

		self.table._database.commit()
		return self.table.get(self.table._pkey == self.pkey_id)


class SaveContainer(EntityExecutableContainer):
	"""UPDATE SQL Query. Used for TableInstance.save()"""

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
			self.table._pkey.escape(getattr(instance, self.table._pkey.name))
		))
		self.execute(commit=True)

		for item in to_update:
			if item:
				item.save()


class RemoveContainer(EntityExecutableContainer):
	"""DELETE SQL Query. Used for TableInstance.remove()"""

	def __init__(self, table, instance):
		super(RemoveContainer, self).__init__(table)
		self += SQLEntity('DELETE FROM')
		self += self.table._sql_entity
		self += SQLEntity('WHERE {0}={1} LIMIT 1'.format(
			self.table._pkey,
			self.table._pkey.escape(getattr(instance, self.table._pkey.name))
		))

		self.execute(commit=True)


def _generative(func):
	"""Chainable method"""
	@wraps(func)
	def decorator(self, *args, **kwargs):
		func(self, *args, **kwargs)
		return self

	return decorator


class ConditionableExecutableContainer(EntityExecutableContainer):
	"""Conditionable query, with where, limit, group, having..."""

	def __init__(self, table, *args, **kwargs):
		super(ConditionableExecutableContainer, self).__init__(table)
		self._where = False
		self._group = False
		self._order = False

	def clone(self):
		return copy.deepcopy(self)

	@_generative
	def where(self, *conditions):
		if self._where is False:
			self += SQLEntity('WHERE')
			self._where = True
		else:
			self += SQLEntity('AND')

		size = len(conditions) - 1
		i = 0

		if size == 0:
			if isinstance(conditions[0], SQLCondition):
				self += conditions[0]
			else:
				self += SQLEntity(conditions[0])
		else:
			for condition in conditions:
				if isinstance(condition, SQLCondition):
					self += SQLEntity('(')
					self += condition
					self += SQLEntity(')')

					if i < size:
						self += SQLEntity('AND')

				i += 1

	@_generative
	def order_by(self, column, order='DESC'):
		if self._order is False:
			self += SQLEntity('ORDER BY')
			self._order = True
		else:
			self += SQLEntity(',')

		if isinstance(column, str):
			self += SQLEntity(column)
		else:
			self += column
			self += SQLEntity(order)

	@_generative
	def group_by(self, group_by):
		if self._group is False:
			self += SQLEntity('GROUP BY')
			self._group = True
		else:
			self += SQLEntity(',')

		if isinstance(group_by, str):
			self += SQLEntity(group_by)

	def limit(self, limit, position=0):
		self += SQLEntity('LIMIT {0},{1}'.format(position, limit))

		if limit == 1:
			return self.execute(unique=True)

		return self.execute()

	def one(self):
		return self.limit(1)

	def all(self):
		return self.execute()


class SelectContainer(ConditionableExecutableContainer):
	"""SELECT SQL Query."""

	def __init__(self, table, *args, **kwargs):
		super(SelectContainer, self).__init__(table)
		self.kwargs = kwargs
		self.args = args
		self.is_count = kwargs.get('is_count') or False
		self.selected = []
		self.add_from = kwargs.get('add_from') or False
		self.executable = True

		# add selected columns
		if self.is_count:
			columns = SQLEntity('COUNT(*)')
		else:
			columns = EntityContainer(separator=',')
			for column in self.table._columns.values() if not args else args:
				columns += column.sql_entities['selection']
				self.selected.append(hash(column))

		# add selected tables
		tables = EntityContainer(separator=',')
		tables += self.table._sql_entity
		if self.add_from:
			tables += SQLEntity(self.add_from)

		# add joins
		joins = EntityContainer()
		for foreign in reversed(self.table._foreigns):
			if hash(foreign['column']) in self.selected or self.is_count:
				join = 'INNER' if foreign['column'].required else 'LEFT'
				joins += SQLJoin(join, foreign['table']._sql_entity, foreign['left_on'], foreign['right_on'])
				if not self.is_count:
					for key, column in foreign['table']._columns.items():
						columns += SQLColumn(
							column.sql_column,
							column.table._db_table,
							'{0}_{1}'.format(foreign['column'].reference, column.sql_column)
						)

		self += SQLEntity('SELECT')

		self += columns

		self += SQLEntity('FROM')
		self += tables

		if len(joins) != 0:
			self += joins

	def execute(self, unique=False):
		cursor = self.table._database.execute(self.sql)
		if self.is_count:
			return cursor.fetchone()[0]
		if unique:
			try:
				return ResultContainer(self.table, cursor).result[0]
			except IndexError:
				return False

		return ResultContainer(self.table, cursor).result

	def count(self):
		self.entities[1] = SQLEntity('COUNT(*)')
		self.is_count = True
		return self.execute()
