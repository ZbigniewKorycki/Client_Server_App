import sqlite3
from sqlite3 import Error


class SQLiteConnection:

    def __init__(self, path):
        self.path = path
        self.create_starting_tables()

    def create_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.path)
            print(sqlite3.version)
        except Error as e:
            print(e)
        else:
            return conn

    def create_table(self, query):
        try:
            conn = self.create_connection()
            cursor = conn.cursor()
            cursor.execute(query)
        except Error as e:
            print(e)

    def create_starting_tables(self):
        self.create_table(query="""CREATE TABLE IF NOT EXISTS server_versions (
                                                                                version VARCHAR(20) PRIMARY KEY,
                                                                                version_date TIMESTAMP);""")
        self.create_table(query="""CREATE TABLE IF NOT EXISTS users (
                                                                            user_id INTEGER,
                                                                            username VARCHAR PRIMARY KEY);""")
        self.create_table(query="""CREATE TABLE IF NOT EXISTS users_privileges (
                                            username VARCHAR PRIMARY KEY,
                                            privileges VARCHAR NOT NULL DEFAULT user,
                                            FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE);""")
        self.create_table(query="""CREATE TABLE IF NOT EXISTS users_passwords (
                                            username VARCHAR PRIMARY KEY,
                                            password VARCHAR NOT NULL,
                                            FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE);""")
        self.create_table(query="""CREATE TABLE IF NOT EXISTS users_messages (
                                        message_id INTEGER PRIMARY KEY,
                                        sender_username VARCHAR NOT NULL,
                                        recipient_username VARCHAR NOT NULL,
                                        message_content VARCHAR(255) NOT NULL,
                                        sending_date TIMESTAMP NOT NULL,
                                        read_by_recipient BOOLEAN DEFAULT false NOT NULL,
                                        FOREIGN KEY (sender_username) REFERENCES users(username) ON DELETE CASCADE,
                                        FOREIGN KEY (recipient_username) REFERENCES users(username) ON DELETE CASCADE);""")


if __name__ == '__main__':
    sql_connection = SQLiteConnection(r"C:\Users\zbign_x5x2ftd\sqlite\db\pythonsqlite.db")
