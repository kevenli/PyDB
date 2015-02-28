'''
'''
import unittest
from PyDB.DbContext import Dialect
import datetime
import PyDB
import time

class Test(unittest.TestCase):


    def setUp(self):
        self.target = Dialect()


    def tearDown(self):
        pass


    def test_datetime_formating(self):
        value = datetime.datetime(2012,3,4, 16,39,43)
        ret = self.target.format_value_string(PyDB.DatetimeField("SomeField"), value)
        self.assertEqual("'2012-03-04 16:39:43'", ret, "Formating invalid")
        #print ret
        datetime.datetime.now()
    
    def test_datetime_formating2(self):
        value = datetime.date(2012, 3, 4)
        ret = self.target.format_value_string(PyDB.DatetimeField("SomeField"), value)
        self.assertEqual("'2012-03-04 00:00:00'", ret, "Formating invalid")
        #print ret
        
    def test_datetime_formating3(self):
        value = time.time()
        ret = self.target.format_value_string(PyDB.DatetimeField("SomeField"), value)
        print ret

if __name__ == "__main__":
    import sys;sys.argv = ['', 'Test.test_datetime_formating3']
    unittest.main()