fysql
=====

Still in developpement

fysql is a small ORM inpired by  `peewee <https://github.com/coleifer/peewee>`_.


Have fun
--------
.. code-block:: python

    >>> from fysql import *

    >>> database = MySQLDatabase('db', host='localhost', user='x', passwd='x')

    >>> class User(Table):
    >>>     db = database
    >>> 
    >>>     firstname = CharColumn(max_length=50)
    >>>     lastname  = CharColumn(max_length=50)
    >>>     role      = CharColumn(index=True, unique=True)

    >>> User.create_table()

    >>> user = User.create(firstname='Fy', lastname='SQL', role='Admin')
    ... # or 
    >>> user = User.get(User.id==1)
    >>> print user
    {"id": 1, "lastname": "SQL", "role": "Admin", "firstname": "Fy"}

    >>> user.role = 'Member'
    >>> user.save() 

    >>> print user
    {"id": 1, "lastname": "SQL", "role": "Member", "firstname": "Fy"}

    >>> # Add new users
    >>> User.create(firstname='Jean', lastname='Bon', role='Member')
    >>> User.create(firstname='Jean', lastname='Rhume', role='Admin')

    >>> users = User.where((User.id==1) | (User.lastname=='Bon')).result
    >>> print users
    [{"id": 1, "lastname": "SQL", "role": "Member", "firstname": "Fy"}, {"id": 2, "lastname": "Bon", "role": "Member", "firstname": "Jean"}]

    >>> count_users = User.count().where(User.role <<< ['Member', 'Admin'])
    >>> print count_users
    3

