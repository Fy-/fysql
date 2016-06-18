# -*- coding: utf-8 -*-
import unittest
from fysql import *

class TestSelect(unittest.TestCase):
    def test_basic_select(self):
        class User(Table):
            db = Database()
            
            firstname = CharColumn()
            lastname  = CharColumn()

        d = User().select().sql
        r = 'SELECT `user`.`id`,`user`.`lastname`,`user`.`firstname` FROM `user`'

        self.assertEqual(d, r)
