# -*- coding: utf-8 -*-
import unittest
from fysql import *

class User(Table):
    db = 'no_db'
    
    firstname = CharColumn()
    lastname  = CharColumn()

    role      = CharColumn(index=True, unique=True)

class Post(Table):
    db = 'no_db'

    title   = CharColumn(default='Post title')
    id_user = FKeyColumn(table=User, reference='user')

class TestCreate(unittest.TestCase):
    def test_create(self):
        d = User.create_db().sql
        r = 'CREATE TABLE IF NOT EXISTS `user` ( `id` bigint(20) UNSIGNED NOT NULL, `lastname` varchar(255) NOT NULL, `role` varchar(190) NOT NULL, `firstname` varchar(255) NOT NULL, PRIMARY KEY (`id`), UNIQUE INDEX `role_index` (`role`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;'

        self.assertEqual(d, r)

    def test_create_fkey(self):
        d = Post.create_db().sql
        r = 'CREATE TABLE IF NOT EXISTS `post` ( `id` bigint(20) UNSIGNED NOT NULL, `id_user` bigint(20) UNSIGNED NOT NULL, `title` varchar(255) NOT NULL DEFAULT \'Post title\', PRIMARY KEY (`id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;'
        
        self.assertEqual(d, r)

    def test_drop(self):
        d = User.drop_db().sql
        r = 'DROP TABLE IF EXISTS `user`;'

        self.assertEqual(d, r)