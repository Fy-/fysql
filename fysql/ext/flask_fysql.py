# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

from ..databases import MySQLDatabase

class FySQL(object):
    engines = {
        'MySQL': MySQLDatabase
    }

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        engine   = self.app.config['DATABASE']['engine']
        db_name  = self.app.config['DATABASE']['db']

        kwargs = {}
        for key, attr in self.app.config['DATABASE'].items():
            if key not in ['engine', 'db']:
                kwargs[key] = attr

        self.engine      = self.engines[engine]

        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def init_db(self):
        return self.engine(self.db_name, **self.conn_kwargs)

    def teardown(self, exception):
        ctx = stack.top
        if hasattr(ctx, 'db'):
            ctx.db.close()

    @property
    def db(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'db'):
                ctx.db = self.init_db()
            return ctx.db
    