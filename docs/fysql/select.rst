.. _select:

Retrieving Data
===============

For all the examples in this sections we will use the following :ref:`complex-table`


Selecting multiple records
--------------------------
You can use :py:meth:`Table.select` to retrieve rows from the tables. :py:meth:`Table.select` always returns a python *list* of :py:class:`Table` instances.

.. code-block:: python

    >>> User.select().result
    [{"id": 1, "lastname": "SQL", "role": "Member", "firstname": "Fy"}, {"id": 2, "lastname": "Bon", "role": "Member", "firstname": "Jean"}]

Selecting a single record
-------------------------
.. code-block:: python

    >>> User.get(User.id == 1)
    {"id": 1, "lastname": "SQL", "role": "Member", "firstname": "Fy"}


Filtering records
-----------------
On :py:meth:`Table.select` and :py:meth:`Table.count` ``limit()`` and/or ``where()`` with :ref:`fysql operators <operators>`.

.. code-block:: python

    >>> User.where(User.id == 2).result
    [{"id": 2, "lastname": "Bon", "role": "Member", "firstname": "Jean"}]

    >>> User.where((User.id == 2) | (User.id==1)).result
    [{"id": 1, "lastname": "SQL", "role": "Member", "firstname": "Fy"}, {"id": 2, "lastname": "Bon", "role": "Member", "firstname": "Jean"}]

    >>> Users.where(User.id << [1,2]))
    [{"id": 1, "lastname": "SQL", "role": "Member", "firstname": "Fy"}, {"id": 2, "lastname": "Bon", "role": "Member", "firstname": "Jean"}]

    >>> Users.where(User.id << [1,2])).limit(1).result
    [{"id": 1, "lastname": "SQL", "role": "Member", "firstname": "Fy"}]

    >>> posts = Post.where(User.firstname.contains('Je')).result
    [{"id": 3, "id_user": 2, "user": {"id": 2, "lastname": "Bon", "role": "Member", "firstname": "Jean"}, "title": "Mon giga post 3"}]
