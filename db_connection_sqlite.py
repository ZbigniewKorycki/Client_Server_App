import sqlite3
from sqlite3 import Error


class SQLiteConnection:

    def __init__(self, db_name):
        self.db_name = db_name
        self.path = fr"C:\Users\zbign_x5x2ftd\sqlite\db\{db_name}"
        self.connection = None
        self.create_connection()
        self.create_starting_tables()

    def create_connection(self):
        try:
            conn = sqlite3.connect(self.path)
        except Error as e:
            print(e)
        else:
            self.connection = conn

    def execute_query(self, query):
        if self.connection is None:
            self.create_connection()
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        connection.close()
        self.connection = None

    def get_all(self, query, params=None):
        if self.connection is None:
            self.create_connection()
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute(query, params)
        items = cursor.fetchall()
        connection.commit()
        connection.close()
        self.connection = None
        return items

    def get_one(self, query, params=None):
        if self.connection is None:
            self.create_connection()
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute(query, params)
        item = cursor.fetchone()
        connection.commit()
        connection.close()
        self.connection = None
        return item

    def delete_query(self, query, params=None):
        if self.connection is None:
            self.create_connection()
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute(query, params)
        item = cursor.fetchone()
        connection.commit()
        connection.close()
        self.connection = None
        return item

    def update_query(self, query, params=None):
        if self.connection is None:
            self.create_connection()
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute(query, params)
        item = cursor.fetchone()
        connection.commit()
        connection.close()
        self.connection = None
        return item

    def insert_query(self, query, params=None):
        if self.connection is None:
            self.create_connection()
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute(query, params)
        item = cursor.fetchone()
        connection.commit()
        connection.close()
        self.connection = None
        return item

    def close_connection_with_db(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def create_starting_tables(self):
        self.execute_query(
            """CREATE TABLE IF NOT EXISTS server_versions (version text PRIMARY KEY, version_date text)""")
        self.execute_query("""CREATE TABLE IF NOT EXISTS users (user_id integer PRIMARY KEY, username text)""")
        self.execute_query(query="""CREATE TABLE IF NOT EXISTS users_privileges (
                                            username text,
                                            privileges text NOT NULL DEFAULT user,
                                            FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE);""")
        self.execute_query(query="""CREATE TABLE IF NOT EXISTS users_passwords (
                                            username text,
                                            password text,
                                            FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE);""")
        self.execute_query(query="""CREATE TABLE IF NOT EXISTS users_messages (
                                        message_id integer PRIMARY KEY,
                                        sender_username text NOT NULL,
                                        recipient_username text NOT NULL,
                                        message_content text NOT NULL,
                                        sending_date text NOT NULL,
                                        read_by_recipient integer DEFAULT 0 NOT NULL,
                                        FOREIGN KEY (sender_username) REFERENCES users(username) ON DELETE CASCADE,
                                        FOREIGN KEY (recipient_username) REFERENCES users(username) ON DELETE CASCADE);""")

        self.execute_query(query="""CREATE TABLE IF NOT EXISTS admin_tokens (
                                                                                token_id text,
                                                                                is_valid text NOT NULL DEFAULT 1);""")


if __name__ == '__main__':
    pass
