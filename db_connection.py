import psycopg2
from db_config import config

config_data = config()


class PostgresSQLConnection:

    def __init__(self):
        self.dbname = config_data['database']
        self.user = config_data['user']
        self.password = config_data['password']
        self.host = config_data['host']
        self.port = config_data['port']
        self.connection = None

    def connect_with_db(self):
        self.connection = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port)

    def execute_query(self, query, params):
        if not self.connection:
            self.connect_with_db()
        self.connection.autocommit = False
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result

    def close_connection_with_db(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def database_transaction(self, query, params):
        try:
            self.connect_with_db()
            result = self.execute_query(query, params)
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error in transaction. Reverting all other operations of a transaction ", error)
            self.connection.rollback()
        else:
            self.connection.commit()
            return result
        finally:
            self.close_connection_with_db()





