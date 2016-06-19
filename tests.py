# -*- coding: utf-8 -*-
import sys, unittest
from tests.test_select import *
from tests.test_where  import *
from tests.test_create import *

from tests.test_db_mysql import *

if __name__ == '__main__':
    unittest.main(argv=sys.argv)