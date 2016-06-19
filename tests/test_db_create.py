# -*- coding: utf-8 -*-
import unittest
from fysql import *

class DevTables(Table):
    db = MySQLDatabase('fysql', host='localhost', user='fysql', passwd='dev')

class User(DevTables):
    firstname = CharColumn()
    lastname  = CharColumn()
    role      = CharColumn(index=True, unique=True)

class Post(DevTables):
    title   = CharColumn(default='Post title')
    id_user = FKeyColumn(table=User, reference='user')

class TestCreate(unittest.TestCase):
    def test_create_drop(self):
        User.create_table()
        Post.create_table()
        d = DevTables._database.get_tables()
        r = '[u\'post\', u\'user\']'

        self.assertEqual(str(d), r)
