# -*- coding: utf-8 -*-
from fysql.databases import MySQLDatabase
from flask import current_app as app

class FySQL(object):
    config = {}
    name = ""
    engine = MySQLDatabase

    def __init__(self, app=None):
        self.app = None
        if app is not None:
            self.init_app(app)


    def init_app(self, app):
        self.config = app.config.get('DATABASE', {})
        self.name = self.config['db']

        self.conn_kwargs = {}
        self.engine = MySQLDatabase
        for key, value in self.config.items():
            if key not in ['engine', 'db']:
                self.conn_kwargs[key] = value

        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

        self.connect()

    def connect(self):
        self.db = self.engine(self.name, **self.conn_kwargs)

    def teardown(self, exception):
        self.db.close()

