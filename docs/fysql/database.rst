.. _database:

Database
========

For now fysql only support MySQL.

.. code-block:: python

    database = MySQLDatabase('mydb', host='localhost', user='x', passwd='x')


.. code-block:: python

    from fysql import *

    class TableA(Table):
        pass

    class TableB(Table):
        pass


.. note::
    For your web-apps you want to open a connection before a request and close it after the response is delivered:

.. code-block:: python

    """
    Flask example
    """

    # Before Request
    @app.before_request
    def before_request():
        database.connect()

    # End of RequestContext lifecycle
    @app.teardown_request
    def teardown_request(exception=None):
        database.close()

.. code-block:: python

    from fysql.databases import MySQLDatabase
    from flask import current_app as app


    class FySQL(object):
        """
        Flask example
        fysql = FySQl(app) or fysql = FySQL() -> fysql.init_app(app)
        """


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

            app.fysql = self
            self.connect()

        def connect(self):
            self.db = self.engine(self.name, **self.conn_kwargs)

        def teardown(self, exception):
            self.db.close()

