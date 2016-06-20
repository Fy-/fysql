fysql
=====

Still in developpement

fysql is a small python ORM inpired by  `peewee <https://github.com/coleifer/peewee>`_.


Have fun
--------
Definition of your tables.

.. code-block:: python

    from fysql import *

    database = MySQLDatabase('db', host='localhost', user='x', passwd='x')

    class User(Table):
        db = database
    
        firstname = CharColumn(max_length=50)
        lastname  = CharColumn(max_length=50)
        role      = CharColumn(index=True, unique=True)

    User.create_table()


Creating your first User.

.. code-block:: python

    >>> user = User.create(firstname='Fy', lastname='SQL', role='Admin')
    >>> print user
    {"id": 1, "lastname": "SQL", "role": "Admin", "firstname": "Fy"}


Updating your User.

.. code-block:: python

    >>> user.role = 'Member'
    >>> user.save() 
    >>> print user
    {"id": 1, "lastname": "SQL", "role": "Member", "firstname": "Fy"}


Selecting one User.

.. code-block:: python

    >>> user = User.get(User.id==1)
    >>> print user
    {"id": 1, "lastname": "SQL", "role": "Admin", "firstname": "Fy"}


Adding new users and selecting members.

.. code-block:: python

    >>> User.create(firstname='Jean', lastname='Bon', role='Member')
    >>> User.create(firstname='Jean', lastname='Rhume', role='Admin')
    >>> users = User.filter(User.role=='Member').all()
    >>> print users
    [{"id": 1, "lastname": "SQL", "role": "Member", "firstname": "Fy"}, {"id": 2, "lastname": "Bon", "role": "Member", "firstname": "Jean"}]


Counting users.

.. code-block:: python

    >>> count_users = User.count_filter(User.role <<< ['Member', 'Admin'])
    >>> print count_users
    3

