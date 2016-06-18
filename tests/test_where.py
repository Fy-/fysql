# -*- coding: utf-8 -*-
import unittest
from fysql import *

class User(Table):
    db = Database()
    
    firstname = CharColumn()
    lastname  = CharColumn()

class Post(Table):
    db = Database()

    title   = CharColumn()
    id_user = FKeyColumn(table=User, reference='users')

class TestWhere(unittest.TestCase):
    def test_where(self):
        d = User.where(User.id==1).sql
        r = 'SELECT `user`.`id` AS user_id,`user`.`lastname` AS user_lastname,`user`.`firstname` AS user_firstname FROM `user` WHERE `user`.`id` = 1'

        self.assertEqual(d, r)

    def test_where_in_int(self):
        d = User.where(User.id << [1,2,3]).sql
        r = 'SELECT `user`.`id` AS user_id,`user`.`lastname` AS user_lastname,`user`.`firstname` AS user_firstname FROM `user` WHERE `user`.`id` IN (1,2,3)'

        self.assertEqual(d, r)

    def test_where_in_char(self):
        d = User.where(User.firstname << ['Florian', 'Nicolas']).sql
        r = 'SELECT `user`.`id` AS user_id,`user`.`lastname` AS user_lastname,`user`.`firstname` AS user_firstname FROM `user` WHERE `user`.`firstname` IN (\'Florian\',\'Nicolas\')'

        self.assertEqual(d, r)

    def test_where_complex(self):
        d = User.where((User.id == 1) & ((User.firstname == User.lastname) | (User.lastname == 'Florian'))).sql
        r = 'SELECT `user`.`id` AS user_id,`user`.`lastname` AS user_lastname,`user`.`firstname` AS user_firstname FROM `user` WHERE (`user`.`id` = 1) AND ((`user`.`firstname` = `user`.`lastname`) OR (`user`.`lastname` = \'Florian\'))'

        self.assertEqual(d, r)

    def test_where_not(self):
        d = User.where((User.id << [1,2]) & ~(User.firstname == 'Florian')).sql
        r = 'SELECT `user`.`id` AS user_id,`user`.`lastname` AS user_lastname,`user`.`firstname` AS user_firstname FROM `user` WHERE (`user`.`id` IN (1,2)) AND (NOT(`user`.`firstname` = \'Florian\'))'

        self.assertEqual(d, r)

    def test_where_multiple(self):
        d =  User.where(User.id==1, User.firstname=='Florian').sql
        r = 'SELECT `user`.`id` AS user_id,`user`.`lastname` AS user_lastname,`user`.`firstname` AS user_firstname FROM `user` WHERE ( `user`.`id` = 1 ) AND ( `user`.`firstname` = \'Florian\' )'

        self.assertEqual(d, r)