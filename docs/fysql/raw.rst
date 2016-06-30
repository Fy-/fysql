.. _raw:

Raw SQL
=======

.. code-block:: python

    query = """SELECT 
            (SELECT COUNT(*) FROM user WHERE status = 'Admin')
            (SELECT COUNT(*) FROM user WHERE status = 'Member')
            (SELECT COUNT(*) FROM user WHERE status = 'Guest') 
        """
        
    >>> print database.raw(query).fetchone()
    [2, 1, 0]
    
    
You can also use RAW SQL in ``select()``, ``where()``, ``group_by()``, ``order_by()``

.. code-block:: python

    folders = Folder.select(
            add_from='folder AS parent'
        ).where(
            'folder.left BETWEEN parent.left AND parent.right'
        ).group_by(
            'folder.id'
        ).order_by(
            'folder.left, folder.id'
        ).all()
        
You can check FyPress models for more examples: https://github.com/Fy-/FyPress/blob/master/fypress/folder/models.py
