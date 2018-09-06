# -*- coding: utf-8 -*-
"""
	fysql.databases
	~~~~~~~~~~~~~~~
	:copyright: (c) 2016 by Gasquez Florian
	:license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
from collections import OrderedDict
from warnings import filterwarnings
from .exceptions import FysqlException

from . import pymysql

class Database(object):

	def __init__(self, database, **kwargs):
		self.conn_kwargs = kwargs
		self.closed = True
		self._connection = False
		self.database = database
		self._tables = OrderedDict()

	@property
	def connection(self):
		if self.closed:
			self._connection = self._connect(self.database, **self.conn_kwargs)
			self.closed = False
		return self._connection

	def create_all(self):
		for key, table in self._tables.items():
			table.drop_table()
			table.create_table()

	def connect(self):
		return self.connection

	def close(self):
		if not self.closed:
			self._close()
			self.closed = True

	def _connect(self, database, **kwargs):
		raise NotImplementedError

	def _close(self):
		raise NotImplementedError

	def _escape_string(self, value):
		raise NotImplementedError

	def escape_string(self, value):
		return self._escape_string(value)


	def cursor(self):
		if self.closed:
			self._connection = self._connect(self.database, **self.conn_kwargs)
			self.closed = False

		return self._connection.cursor()

	def insert_id(self, cursor):
		return self._insert_id(cursor)

	def commit(self):
		self.connection.commit()

	def rollback(self):
		self.connection.rollback()

	def raw(self, sql, commit=False):
		return self.execute(sql, commit)

	def execute(self, sql, commit=False):
		cursor = self.cursor()
		cursor.execute(sql)
		if commit:
			self.commit()

		return cursor


class MySQLDatabase(Database):

	def _connect(self, database, **kwargs):


		conn_kwargs = {'charset': 'utf8', 'use_unicode': True}
		conn_kwargs.update(kwargs)

		return pymysql.connect(
			host=conn_kwargs['host'],
			user=conn_kwargs['user'],
			password=conn_kwargs['password'],
			db=database,
			charset='utf8mb4'
		)

	def _close(self):
		self.connection.close()

	def _insert_id(self, cursor):
		return cursor.get_last_id()

	def _row_count(self, cursor):
		return cursor.rowcount

	def _escape_string(self, value):
		
		#return self.connection.escape_string(value)
		#return value.encode('raw_unicode_escape')
		return self.connection.escape_string(value) 

	def get_tables(self):
		return [row for row, in self.execute('SHOW TABLES')]
