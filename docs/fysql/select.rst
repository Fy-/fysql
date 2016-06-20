.. _select:

Retrieving Data
===============

For all the examples in this sections we will use the following :ref:`complex-table`


Selecting multiple records
--------------------------
You can use :py:meth:`Table.select` to retrieve rows from the tables. :py:meth:`Table.select` always returns a python *list* of :py:class:`Table` instances.

.. code-block:: python

    >>> User.select().all() # or User.all()
    [{"id": 1, "lastname": "SQL", "role": "Member", "firstname": "Fy"}, {"id": 2, "lastname": "Bon", "role": "Member", "firstname": "Jean"}]

Selecting a single record
-------------------------
.. code-block:: python

    >>> User.get(User.id == 1)
    {"id": 1, "lastname": "SQL", "role": "Member", "firstname": "Fy"}

Filtering records
-----------------
On :py:meth:`Table.select` and :py:meth:`Table.count` you can use ``limit()`` and/or ``where()/filter()`` with :ref:`fysql operators <operators>`.

.. code-block:: python

    >>> print User.filter(User.id == 2).all()
    [{"id": 2, "lastname": "Bon", "role": "Member", "firstname": "Jean"}]

    >>> print User.filter((User.id == 2) | (User.id==1)).all()
    [{"id": 1, "lastname": "SQL", "role": "Member", "firstname": "Fy"}, {"id": 2, "lastname": "Bon", "role": "Member", "firstname": "Jean"}]

    >>> print Users.filter(User.id << [1,2]).all()
    [{"id": 1, "lastname": "SQL", "role": "Member", "firstname": "Fy"}, {"id": 2, "lastname": "Bon", "role": "Member", "firstname": "Jean"}]

    >>> print Users.filter(User.id << [1,2]).limit(1)
    [{"id": 1, "lastname": "SQL", "role": "Member", "firstname": "Fy"}]

    >>> print Post.filter(User.firstname.contains('Je')).all()
    [{"id": 3, "id_user": 2, "user": {"id": 2, "lastname": "Bon", "role": "Member", "firstname": "Jean"}, "title": "Mon giga post 3"}]

Custom Selection
----------------
You can do custom select on your tables, it will also return a python *list* of :py:class:`Table` instances with only the selected values.

.. code-block:: python
   >>> print User.select(User.id, User.lastname).where(User.lastname=='Bon').all()
   [{"id": 2, "lastname": "Bon", "role": "Member", "firstname": "Jean"}]

   >>> print User.select(User.id, User.lastname).where(User.lastname << ['Bon', 'SQL']).limit(1)
   [{"id": 1, "lastname": "SQL", "role": "Member", "firstname": "Fy"}]