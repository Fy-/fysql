.. _update:

Updating/Deleting Data
======================
For all the examples in this sections we will use the following :ref:`complex-table`

Adding data
-----------
Two ways to add items with FySQL, you can user :py:meth:`Table.create`, or :py:meth:`TableInstance.insert`.

.. code-block:: python

    >>> print User.create('firstname'='TestFirstName', 'lastname'='TestLastName', role='Admin')
    {"id": 3, "lastname": "TestLastName", "role": "Admin", "firstname": "TestFirstName"}

.. code-block:: python
    user = User()
    user.firstname = 'TestFirstName'
    user.lastname  = 'TestLastName'
    user.role      = 'Admin'
    >>> print user.insert()
    
    {"id": 3, "lastname": "TestLastName", "role": "Admin", "firstname": "TestFirstName"}
    
Saving data
-----------
py:meth:`TableInstance.save`

.. code-block:: python
    user = User.get(User.id==3)
    user.role = 'Member'
    user.save()
    
    >>> print user
    {"id": 3, "lastname": "TestLastName", "role": "Member", "firstname": "TestFirstName"}
    

Deleting data
-------------
py:meth:`TableInstance.save`
.. code-block:: python
    user = User.get(User.id==3)
    user.remove()
