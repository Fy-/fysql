# -*- coding: utf-8 -*-
import unittest
from fysql import *

class User(Table):
    db = 'no_db'
    
    firstname = CharColumn()
    lastname  = CharColumn()

class Post(Table):
    db = 'no_db'

    title   = CharColumn()
    id_user = FKeyColumn(table=User, reference='user')

class TestSelect(unittest.TestCase):
    def test_basic_select(self):
        d = User().select().sql
        r = 'SELECT `user`.`id` AS user_id,`user`.`lastname` AS user_lastname,`user`.`firstname` AS user_firstname FROM `user`'

        self.assertEqual(d, r)

    def test_fkey_select(self):
        d = Post.select().sql
        r = 'SELECT `post`.`id` AS post_id,`post`.`id_user` AS post_id_user,`post`.`title` AS post_title,`user`.`id` AS user_id,`user`.`lastname` AS user_lastname,`user`.`firstname` AS user_firstname FROM `post` INNER JOIN `user` ON `post`.`id_user`=`user`.`id`'

        self.assertEqual(d, r)

    def test_single_column_select(self):
        d = Post.select(Post.title).sql
        r = 'SELECT `post`.`title` AS post_title FROM `post`'

        self.assertEqual(d, r)

    def test_fkey_filter(self):
        d = Post.filter(User.id==1).sql
        r = 'SELECT `post`.`id` AS post_id,`post`.`id_user` AS post_id_user,`post`.`title` AS post_title,`user`.`id` AS user_id,`user`.`lastname` AS user_lastname,`user`.`firstname` AS user_firstname FROM `post` INNER JOIN `user` ON `post`.`id_user`=`user`.`id` WHERE `user`.`id` = 1'

        self.assertEqual(d, r)



