.. _operators:

Operators
=========
The following types of comparaisons are supported by fysql

======================= =================================================
Operator                Information
======================= =================================================
``==``                  x equals y
``!=``                  x is not equal to y
``<``                   x is less than y
``<=``                  x is less or equal to y
``>``                   x is greater than y
``>=``                  x is greater or equal to y
``<<``                  x IN y, where y is a list
``%``                   x LIKE y where y may contain wildcards
``.contains(substr)``   Wild-card search for a substring
``.startswith(prefix)`` Search for values beginning with ``prefix``.
``.endswith(suffix)``   Search for values ending with ``suffix``.
======================= =================================================

To combine clauses using logical operators use:

================ ==================== =============================================================
Operator         Information          Example
================ ==================== =============================================================
``&``            AND                  ``(User.id == 1) & 'User.username == 'testuser1')``     
``|``            OR                   ``(User.id == 1) | (User.id == 2)``
``~``            NOT                  ``~(User.username << ['testuser2','testuser3'])``
================ ==================== =============================================================