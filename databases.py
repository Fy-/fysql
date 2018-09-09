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
import mysql.connector as mysql_connector
from .exceptions import FysqlException
from .tables import Tables
from .static import Tables


class Database(object):

	def __init__(self, database, **kwargs):
		self.conn_kwargs = kwargs
		self.closed = True
		self._connection = False
		self.database = database
		
		for key, value in Tables.tables.items():
			value._database = self

	@property
	def connection(self):
		if self.closed:
			self._connection = self._connect(self.database, **self.conn_kwargs)
			self.closed = False
		return self._connection

	def create_all(self, ignore=[]):
		for key, table in Tables.tables.items():
			print(table)
			if table not in ignore:
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


		conn_kwargs = {'charset': 'utf8mb4', 'use_unicode': True}
		conn_kwargs.update(kwargs)

		return mysql_connector.connect(
			host=conn_kwargs['host'],
			user=conn_kwargs['user'],
			password=conn_kwargs['password'],
			db=database,
			charset=conn_kwargs['charset'],
		)

	def _close(self):
		self.connection.close()

	def _insert_id(self, cursor):
		return cursor.lastrowid 

	def _row_count(self, cursor):
		return cursor.rowcount

	def _escape_string(self, value):
		_escape_table = [chr(x) for x in range(128)]
		_escape_table[0] = u'\\0'
		_escape_table[ord('\\')] = u'\\\\'
		_escape_table[ord('\n')] = u'\\n'
		_escape_table[ord('\r')] = u'\\r'
		_escape_table[ord('\032')] = u'\\Z'
		_escape_table[ord('"')] = u'\\"'
		_escape_table[ord("'")] = u"\\'"

		def _escape_unicode(value):
			"""escapes *value* without adding quote.
			Value should be unicode
			"""
			return value.translate(_escape_table)
		

		return _escape_unicode(value)

		#return value.encode('raw_unicode_escape')

	def get_tables(self):
		return [row for row, in self.execute('SHOW TABLES')]
