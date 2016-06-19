.. _columns:

Columns
=======

A :py:class:`Column` represents a column on a database table.

============================== =================
ColumnType                     MySQL
============================== =================
:py:class:`IntegerColumn`      integer
:py:class:`TinyIntegerColumn`  tinyint
:py:class:`BigIntegerColumn`   bigint
:py:class:`SmallIntegerColumn` smallint
:py:class:`BooleanColumn`      tinyint
:py:class:`PKeyColumn`         integer
:py:class:`FKeyColumn`         integer
:py:class:`FloatColumn`        real
:py:class:`DoubleColumn`       double precision
:py:class:`DateTimeColumn`     datetime
:py:class:`DateColumn`         date
:py:class:`TimeColumn`         time
:py:class:`CharColumn`         varchar
:py:class:`TextColumn`         longtext
============================== =================

Special columns
^^^^^^^^^^^^^^^
========================= ================= ==================================================
Column Type               Database          Information
========================= ================= ==================================================
:py:class:`VirtualColumn` None              Represents a :py:class:`Table` instance
========================= ================= ==================================================

Columns parameters
^^^^^^^^^^^^^^^^^^
========================= =================================================================
Parameter                 Description
========================= =================================================================
``null = False``          boolean indicating if null values are allowed to be stored.
``index = False``         boolean indicating to create an index on this column.
``unique = False``        boolean indicating to create a unique index on this column. 
``default = None``        any value to use as a default.
``pkey = False``          whether this field is the primary key for the table.
``db_column = None``      string representing the database column to use if different.
========================= =================================================================

Special parameters
^^^^^^^^^^^^^^^^^^

+--------------------------------+------------------------------------------------+
| Column Type                    | Special Paramaters                             |
+--------------------------------+------------------------------------------------+
| :py:class:`CharColumn`         | ``max_length``                                 |
+--------------------------------+------------------------------------------------+
| :py:class:`DateTimeColumn`     | ``format``                                     |
+--------------------------------+------------------------------------------------+
| :py:class:`DateColumn`         | ``format``                                     |
+--------------------------------+------------------------------------------------+
| :py:class:`TimeColumn`         | ``format``                                     |
+--------------------------------+------------------------------------------------+
| :py:class:`FKeyColumn`         | ``reference``                                  |
+--------------------------------+------------------------------------------------+
