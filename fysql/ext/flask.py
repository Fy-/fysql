# -*- coding: UTF-8 -*-

from ..databases import MySQLDatabase



class FlaskFySQL(object):
    engines = {
        'MySQL': MySQLDatabase
    }

    def __init__(self, app=None):
        self.app = app
        if self.app is not None:
            self.init_app(app)

    def init_app(self, app):
        kwargs   = self.app.config['DATABASE']
        engine   = self.app.config['DATABASE']['engine']
        db_name  = self.app.config['DATABASE']['db']
        del kwargs['engine']
        del kwargs['db']

        self.conn_kwargs = kwargs
        self.db_name     = db_name
        self.engine      = self.engines[engine]
        self.db          = self.engine(self.db_name, **self.conn_kwargs)

        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.close)
        else:
            app.teardown_request(self.close)

        self.connect()

    def connect(self):
        return self.db.connect()

    def close(self, exception):
        return self.db.close()
