import unittest
from db_connection import PostgresSQLConnection
import psycopg2


class TestDataBaseConnection(unittest.TestCase):

    def setUp(self):
        self.db = PostgresSQLConnection(dbname="test_db")

    def tearDown(self):
        result = self.db.database_transaction(
            query="""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
        table_names = [table_name[0] for table_name in result]
        for table in table_names:
            self.db.database_transaction(f"""DROP TABLE IF EXISTS {table} CASCADE;""")

    def test_open_close_connection_with_db(self):
        self.assertEqual(self.db.connection, None)
        self.db.connect_with_db()
        self.assertNotEqual(self.db.connection, None)
        self.assertIsInstance(self.db.connection, psycopg2.extensions.connection)
        self.db.close_connection_with_db()
        self.assertEqual(self.db.connection, None)
        self.assertNotIsInstance(self.db.connection, psycopg2.extensions.connection)

    def test_database_transaction(self):
        result_incorrect_syntax = self.db.database_transaction("""INCORRECT QUERY test_table VALUES ("value");""")
        result_table_dont_exists = self.db.database_transaction(
                    query="""INSERT INTO test_table VALUES (%s, %s);""",
                    params=("1.9", 199))
        self.assertFalse(result_incorrect_syntax)
        self.assertFalse(result_table_dont_exists)












if __name__ == '__main__':
    unittest.main()
