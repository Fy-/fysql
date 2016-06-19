# -*- coding: utf-8 -*-
import unittest
from fysql import *

database =  MySQLDatabase('fysql', host='localhost', user='fysql', passwd='dev')

class DevTables(Table):
    db = database

class User(DevTables):
    firstname = CharColumn(max_length=150)
    lastname  = CharColumn(max_length=150)
    role      = CharColumn(index=True, unique=True)

class Post(DevTables):
    title   = CharColumn(default='Post title', max_length=255)
    id_user = FKeyColumn(table=User, reference='user')

class TestMySQL(unittest.TestCase):
    def test1_create_drop(self):
        User.create_table()
        Post.create_table()
        d = str(database.get_tables())
        r = '[u\'post\', u\'user\']'

        self.assertEqual(d, r)

    def test2_create_all(self):
        database.create_all()
        d = str(database.get_tables())
        r = '[u\'post\', u\'user\']'

        self.assertEqual(d, r)

    def test3_insert_select(self):
        user1 = User.create(firstname='Florian', lastname='Gasquez', role='Admin')
        user2 = User.create(firstname='Jean', lastname='Bon', role='Noob')

        Post.create(title='Mon super post 1', id_user=user1.id)
        Post.create(title='Mon super post 2', id_user=user2.id)
        Post.create(title='Mon super post 3', id_user=user1.id)

        d = str(User.select().result) + str (Post.select().result)
        r = '[{"id": 1, "lastname": "Gasquez", "role": "Admin", "firstname": "Florian"}, {"id": 2, "lastname": "Bon", "role": "Noob", "firstname": "Jean"}][{"id": 1, "id_user": 1, "user": {"id": 1, "lastname": "Gasquez", "role": "Admin", "firstname": "Florian"}, "title": "Mon super post 1"}, {"id": 2, "id_user": 2, "user": {"id": 2, "lastname": "Bon", "role": "Noob", "firstname": "Jean"}, "title": "Mon super post 2"}, {"id": 3, "id_user": 1, "user": {"id": 1, "lastname": "Gasquez", "role": "Admin", "firstname": "Florian"}, "title": "Mon super post 3"}]'

        self.assertEqual(d, r)

    def test4_get_update(self):
        post = Post.get(Post.id==3)
        post.title = 'Mon giga post 3'
        post.user.lastname = 'Haha!'
        post.save()

        d = repr(post)
        r = '{"id": 3, "id_user": 1, "user": {"id": 1, "lastname": "Haha!", "role": "Admin", "firstname": "Florian"}, "title": "Mon giga post 3"}'

        self.assertEqual(d, r)

    def test5_count_all(self):
        d = Post.count_all()
        r = 3

        self.assertEqual(d, r)

    def test6_count_where(self):
        d = Post.count().where(User.id==1).result
        r = 2
        self.assertEqual(d, r)

    def test7_remove(self):
        post = Post.get(Post.id==3)
        post.remove()

        d = Post.get(Post.id==3)
        r = False

        self.assertEqual(d, r)
