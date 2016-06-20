.. fysql documentation master file, created by
   sphinx-quickstart on Mon Jun 13 21:22:18 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :hidden:
   
   Database <fysql/database>
   Tables <fysql/tables>
   Columns <fysql/columns>
   Retrieving Data <fysql/select>
   Updating/Deleting Data <fysql/update>
   Operators <fysql/operators>

fysql
=====

Still in developpement

fysql is a small ORM inpired by  `peewee <https://github.com/coleifer/peewee>`_.


Have fun
--------
.. code-block:: python

    from fysql import *

    database = MySQLDatabase('db', host='localhost', user='x', passwd='x')

    class User(Table):
        db = database

        firstname = CharColumn(max_length=50)
        lastname  = CharColumn(max_length=50)
        role      = CharColumn(index=True, unique=True)

    User.create_table()

    user = User.create(firstname='Fy', lastname='SQL', role='Admin')
    # or 
    user = User.get(User.id==1)

.. code-block:: python

  >>> print user
  {"id": 1, "lastname": "SQL", "role": "Admin", "firstname": "Fy"}

.. code-block:: python

    user.role = 'Member'
    user.save() 

>>> print user
{"id": 1, "lastname": "SQL", "role": "Member", "firstname": "Fy"}

.. code-block:: python

    # Add new users
    User.create(firstname='Jean', lastname='Bon', role='Member')
    User.create(firstname='Jean', lastname='Rhume', role='Admin')

    users = User.where((User.id==1) | (User.lastname=='Bon')).result

.. code-block:: python

    >>> print users
    [{"id": 1, "lastname": "SQL", "role": "Member", "firstname": "Fy"}, {"id": 2, "lastname": "Bon", "role": "Member", "firstname": "Jean"}]

.. code-block:: python

    count_users = User.count().where(User.role <<< ['Member', 'Admin'])

.. code-block:: python

    >>> print count_users
    3



Note
----
If you find any bugs you can contact me via `github <https://github.com/Fy-Network/fysql>`_ or `IRC <irc://freenode.net/fy>`_.


