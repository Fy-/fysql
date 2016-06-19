.. _database:

Database
========

For now fysql only support MySQL.

.. code-block:: python

    database = MySQLDatabase('mydb', host='localhost', user='x', passwd='x')

The easy way:

.. code-block:: python

    from fysql import *

    class TableA(Table):
        db = database

    class TableB(Table):
        db = database


The good way to do this is to create a base class and all your tables will extend it.

.. code-block:: python
    
    class MyDBTables(Table):
        db = database

    class TableA(MyDBTables): pass
    class TableB(MyDBTables): pass


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