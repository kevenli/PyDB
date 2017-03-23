'''

'''
import unittest
import PyDB
import logging
import datetime
from PyDB.exceptions import *

manager_dburl = 'oracle://sys:Welcome01@10.10.10.5/test.oracle.com'
test_dburl = 'oracle://pydb_test:testing@10.10.10.5/test.oracle.com'

sql_create_table1 = '''
CREATE TABLE pydb_test.table1 (
  id number constraint table_pk primary key,
  fint number NULL,
  fstr varchar2(50) NULL,
  flong number(20) NULL,
  fdate date NULL,
  fdatetime date NULL
)
'''

sql_create_table2 =         """
            create table pydb_test.table2 (
                k1 int not null,
                k2 int not null,
                CONSTRAINT table2_pk PRIMARY KEY (k1, k2)
            )
        """

sql_create_users = '''
            create table pydb_test.users (
                id int constraint users_pk primary key,
                username varchar(20) not null,
                constraint users_uk_username unique (username)
            )
'''

def setup_module():
    import cx_Oracle
    sys_maanger_context = PyDB.OracleContext(manager_dburl, mode=cx_Oracle.SYSDBA)
    try:
        sys_maanger_context.execute_sql("drop user pydb_test cascade")
    except:
        pass
    sys_maanger_context.execute_sql("create user pydb_test identified by testing")
    sys_maanger_context.execute_sql('alter user pydb_test quota 4 m on "USERS"')
    sys_maanger_context.execute_sql('grant create table to pydb_test')
    sys_maanger_context.execute_sql('grant create session to pydb_test')
    sys_maanger_context.execute_sql(sql_create_table1)
    sys_maanger_context.execute_sql(sql_create_table2)
    sys_maanger_context.execute_sql(sql_create_users)
    sys_maanger_context.close()

def teardown_module():
    import cx_Oracle
    sys_maanger_context = PyDB.OracleContext(manager_dburl, mode=cx_Oracle.SYSDBA)
    sys_maanger_context.execute_sql('drop user pydb_test cascade')
    sys_maanger_context.close()



#@unittest.skip
class Test(unittest.TestCase):
    def setUp(self):
        self.target = PyDB.OracleContext(test_dburl)
        self.target.execute_sql('delete from table1')
        logging.basicConfig(level=logging.DEBUG)

    def tearDown(self):
        self.target.close()
        self.target = None

    def test_load_metadata(self):
        context = self.target
        fields = context.load_metadata("TABLE1")
        
        for field in fields:
            print field

    def test_save(self):
        context = self.target
        tablename = 'table1'
        context.set_metadata(tablename, [
            PyDB.IntField("id", is_key=True),
            PyDB.StringField("fstr"),
            PyDB.IntField("fint")
        ])

        data = {"id": 1, "fint": 1, "fstr": 'abc'}
        context.save(tablename, data)
        context.commit()

        row = context.get(tablename, {'id': 1})
        logging.debug(row)
        self.assertIsNotNone(row)
        self.assertEqual(row['fstr'], 'abc')
        self.assertEqual(row['fint'], 1)

    def test_save_tablename_insentisive(self):
        context = self.target
        tablename = 'table1'
        tablename_upper = 'TABLE1'
        context.set_metadata(tablename, [
            PyDB.IntField("id", is_key=True),
            PyDB.StringField("fstr"),
            PyDB.IntField("fint")
        ])

        data = {"id": 1, "fint": 1, "fstr": 'abc'}
        context.save(tablename_upper, data)
        context.commit()

        row = context.get(tablename_upper, {'id': 1})
        logging.debug(row)
        self.assertIsNotNone(row)
        self.assertEqual(row['fstr'], 'abc')
        self.assertEqual(row['fint'], 1)
        
    def test_save_update(self):
        context = self.target
        tablename = 'table1'
        context.set_metadata(tablename, [
            PyDB.IntField("id", is_key=True),
            PyDB.StringField("fstr"),
            PyDB.IntField("fint")
        ])

        data = {"id": 1, "fint": 1, "fstr": 'abc'}
        context.save(tablename, data)

        data['fint'] = 2
        data['fstr'] = 'abcd'
        context.save(tablename, data)

        row = context.get(tablename, {'id': 1})
        self.assertIsNotNone(row)
        self.assertEqual(row['fstr'], 'abcd')
        self.assertEqual(row['fint'], 2)

    def test_set_metadata(self):
        context = self.target
        context.set_metadata("table1", [
                                        PyDB.IntField("id", is_key = True)
                                        ])
        data = {"id": 1, "fielda" : 'a'}
        tablename = 'table1'
        context.save(tablename, data)

    def test_load_metadata_default_primarykey(self):
        context = self.target
        fields = context.load_metadata('table1')
        self.assertEqual(len(fields), 6)

        self.assertEqual('ID', fields[0].name)
        self.assertTrue(fields[0].is_key)
        self.assertEqual(type(fields[0]), PyDB.IntField)

        self.assertEqual('FLONG', fields[1].name)
        self.assertFalse(fields[1].is_key)
        self.assertEqual(type(fields[1]), PyDB.DecimalField)

        self.assertEqual('FINT', fields[2].name)
        self.assertFalse(fields[2].is_key)
        self.assertEqual(type(fields[2]), PyDB.IntField)

        self.assertEqual('FDATETIME', fields[3].name)
        self.assertFalse(fields[3].is_key)
        self.assertEqual(type(fields[3]), PyDB.DatetimeField)

        self.assertEqual('FSTR', fields[4].name)
        self.assertFalse(fields[4].is_key)
        self.assertEqual(type(fields[4]), PyDB.StringField)

        self.assertEqual('FDATE', fields[5].name)
        self.assertFalse(fields[5].is_key)
        self.assertEqual(type(fields[5]), PyDB.DatetimeField)

    def test_load_metadata_uniquekey(self):
        context = self.target
        fields = context.load_metadata('users', key_type=PyDB.KEY_TYPE_UNIQUE_KEY)
        self.assertEqual(len(fields), 2)

        # keys go first
        self.assertEqual('USERNAME', fields[0].name)
        self.assertTrue(fields[0].is_key)
        self.assertEqual(type(fields[0]), PyDB.StringField)

        self.assertEqual('ID', fields[1].name)
        self.assertFalse(fields[1].is_key)
        self.assertEqual(type(fields[1]), PyDB.IntField)

    def test_load_metadata2(self):
        context = self.target
        fields = context.load_metadata('table1')
        fields = context.set_metadata('table1', fields)
        for field in fields.values():
            print field

        self.assertTrue(fields['ID'].is_key)

    def test_save2(self):
        context = self.target
        tablename = 'table1'
        context.set_metadata(tablename, context.load_metadata(tablename))
        data = {"fint": 1, "fstr": 'ab\'c'}
        try:
            context.save(tablename, data)
            self.fail('Did not catch the exception.')
        except TableKeyNotSpecified:
            pass

    def test_product_database_types(self):
        context = self.target
        cursor = context.execute_sql("select table_name from user_tables")
        rows = cursor.fetchall()

        for row in rows:
            context.load_metadata(row[0])
            print row

    def test_save_or_update(self):
        context = self.target
        tablename = 'table1'
        context.set_metadata(tablename, context.load_metadata(tablename))
        data = {
                "id" : 1,
                "fint": 2,
                "fstr": 'abc',
                'fdate': datetime.date.today(),
                'fdatetime': datetime.datetime.now()}
        context.save_or_update(tablename, data)
        context.commit()

    def test_get_1(self):
        context = self.target
        tablename = 'table1'
        context.set_metadata(tablename, context.load_metadata(tablename))
        id = 1
        data = {'id':id}
        context.save(tablename, data)
        row = context.get(tablename, {'id' : id})
        logging.debug(row)
        self.assertEqual(id, row['id'], 'Result rows id is not %s' % id)

    def test_save_10000_batch(self):
        context = self.target
        tablename = 'table1'
        context.set_metadata(tablename, context.load_metadata(tablename))
        rows = []
        for i in xrange(10000):
            data = {'id': i, "fint": 1, "fstr": 'ab\'c'}
            rows.append(data)
        context.save_batch(tablename, rows)

    def test_exists_key(self):
        context = self.target
        tablename = 'table2'
        keys = {'k1' : 1, 'k2' : 2}

        context.set_metadata(tablename, context.load_metadata(tablename))
        context.save(tablename, keys)
        self.assertTrue(context.exists_key(tablename, keys))

    def test_not_existing_table_metadata(self):
        context = self.target
        tablename = 'table_not_existing'
        try:
            context.load_metadata(tablename)
            self.fail('Should raise TableNotExistError here')
        except TableNotExistError:
            pass

if __name__ == "__main__":
    import sys;sys.argv = ['', 'Test.test_save_or_update']
    unittest.main()