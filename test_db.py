import unittest
from db_connection import PostgresSQLConnection
import psycopg2

class TestDataBaseConnection(unittest.TestCase):

    def setUp(self):
        self.db = PostgresSQLConnection(dbname="test_db")

    def test_open_close_connection_with_db(self):
        self.assertEqual(self.db.connection, None)
        self.db.connect_with_db()
        self.assertNotEqual(self.db.connection, None)
        self.assertIsInstance(self.db.connection, psycopg2.extensions.connection)
        self.db.close_connection_with_db()
        self.assertEqual(self.db.connection, None)
        self.assertNotIsInstance(self.db.connection, psycopg2.extensions.connection)







if __name__ == '__main__':
    unittest.main()
