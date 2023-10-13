from datetime import datetime
import random
import string
from db_connection import PostgresSQLConnection

INBOX_UNREAD_MESSAGES_LIMIT_FOR_USER = 5


class Server:
    def __init__(self, host, port, buffer, start_version="0.1.0"):
        self.host = host
        self.port = port
        self.buffer = buffer
        self.db = PostgresSQLConnection()
        self.create_db_tables()
        self.add_server_version(start_version)

    def create_db_tables(self):
        self.db.database_transaction(query="""CREATE TABLE IF NOT EXISTS server_versions (
                                                    version VARCHAR(20) PRIMARY KEY,
                                                    version_date TIMESTAMP);""")
        self.db.database_transaction(query="""CREATE TABLE IF NOT EXISTS users_privileges (
                                                                                    username VARCHAR PRIMARY KEY,
                                                                                    privilege VARCHAR NOT NULL DEFAULT user
                                                                                    );""")
        self.db.database_transaction(query="""CREATE TABLE IF NOT EXISTS users_passwords (
                                                                                    username VARCHAR PRIMARY KEY,
                                                                                    password VARCHAR NOT NULL
                                                                                    );""")
        self.db.database_transaction(query="""CREATE TABLE IF NOT EXISTS users_messages (
                                                                        message_id SERIAL PRIMARY KEY,
                                                                        sender_username VARCHAR NOT NULL,
                                                                        recipient_username VARCHAR NOT NULL,
                                                                        message_content VARCHAR(255) NOT NULL,
                                                                        sending_date TIMESTAMP NOT NULL,
                                                                        read_by_recipient BOOLEAN DEFAULT false NOT NULL
                                                                        );""")

    def get_server_versions(self):
        versions = self.db.database_transaction(query="""SELECT * FROM server_versions;""")
        return versions

    def add_server_version(self, version_num):
        version_num_occurrence = self.db.database_transaction(
            query="""SELECT COUNT(*) FROM server_versions WHERE version = %s;""",
            params=(version_num,))
        if version_num_occurrence[0][0] == 0:
            self.db.database_transaction(
                query="""INSERT INTO server_versions VALUES (%s, %s);""",
                params=(version_num, str(datetime.now().strftime("%d/%m/%Y, %H:%M"))))
            message = {f"Success": f"New server version: {version_num}, has been added."}
        else:
            message = {f"Duplicate": f"Server version: {version_num}, already exists."}
        return message

    def get_server_uptime(self):
        current_time = datetime.now()
        server_time = self.db.database_transaction(
            query="""SELECT version_date FROM server_versions ORDER BY version_date DESC;""")
        server_time_datetime = datetime.strptime(str(server_time[0][0]), '%Y-%m-%d %H:%M:%S')
        server_uptime = current_time - server_time_datetime
        return server_uptime

    def add_user(self, username, privilege="user"):
        if self.check_if_username_exists(username):
            error_message_user_duplicate = {
                "User duplicate": "The user with this name exists already, choose another username."
            }
            return error_message_user_duplicate
        elif username == "":
            error_message_empty_username = {
                "Empty username": "The username must not be empty."
            }
            return error_message_empty_username
        elif not username[0].isalpha():
            error_message_start_with_alpha = {
                "Incorrect username": "The username have to start with a letter (a-z/A-Z)."
            }
            return error_message_start_with_alpha
        elif " " in username:
            error_message_have_space = {
                "No space in username allowed": "The username must not contain any space."
            }
            return error_message_have_space
        else:
            if privilege != "admin":
                privilege = "user"
            password = self.password_generator()
            self.db.database_transaction(query="""INSERT INTO users_passwords VALUES (%s, %s);""",
                                         params=(username, password))
            self.db.database_transaction(query="""INSERT INTO users_privileges VALUES (%s, %s);""",
                                         params=(username, privilege))

            print(password)
            success_message = {
                "User added": f"'{username}' has been successfully added do database."
            }
            return success_message

    def password_generator(self):
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for i in range(12))
        return password

    def login_into_system(self, username, password):
        result = self.db.database_transaction(
            query="""SELECT FROM users_passwords WHERE username = %s AND password = %s;""",
            params=(username, password))
        if result:
            return True
        else:
            return False

    def check_if_username_exists(self, username):
        result = self.db.database_transaction(
            query="""SELECT COUNT(*) FROM users_privileges WHERE username = %s;""",
            params=(username,))
        # output from result in format [(1,)] if username exists or [(0,)] if not exists
        if result[0][0]:
            return True
        else:
            return False

    def user_base_interface(self, username):
        inbox_info = f"In your inbox you have: xxxxxxxxxx unread messages."
        return username, inbox_info

    def send_message(self, sender_username, recipient_username, message):
        if not self.check_if_username_exists(recipient_username):
            error_message_no_recipient = {
                "No recipient": "Recipient with given username don't exist."
            }
            return error_message_no_recipient
        else:
            if len(message) <= 255:
                if (self.count_unread_messages_in_username_inbox(
                        recipient_username) < INBOX_UNREAD_MESSAGES_LIMIT_FOR_USER) or (
                        self.check_if_user_has_admin_privilege(recipient_username)):
                    self.db.database_transaction(query="""INSERT INTO users_messages(sender_username, recipient_username, message_content, sending_date)
                                    VALUES (%s, %s, %s, %s);""", params=(
                        sender_username,
                        recipient_username,
                        message,
                        datetime.now().strftime("%d/%m/%Y, %H:%M")))
                    success_message_sent = {
                        "Message sent": "The message has been successfully sent."
                    }
                    return success_message_sent
                else:
                    error_message_recipient_inbox_limit = {
                        "Inbox limit": "The recipient has reached the message limit in the inbox."
                    }
                    return error_message_recipient_inbox_limit
            else:
                error_message_over_255_characters = {
                    "Character limit reached": "Message is too long (max. 255 characters)."
                }
                return error_message_over_255_characters

    def send_message_to_all(self, sender_username, message):
        messages_stats = []
        if len(message) <= 255:
            for recipient_username in self.get_all_users_list():
                if recipient_username != sender_username:
                    if (self.count_unread_messages_in_username_inbox(
                            recipient_username) < INBOX_UNREAD_MESSAGES_LIMIT_FOR_USER) or (
                            self.check_if_user_has_admin_privilege(recipient_username)):
                        self.db.database_transaction(query="""INSERT INTO users_messages(sender_username, recipient_username, message_content, sending_date)
                                                            VALUES (%s, %s, %s, %s);""", params=(
                            sender_username,
                            recipient_username,
                            message,
                            datetime.now().strftime("%d/%m/%Y, %H:%M")))
                        result = {"recipient": recipient_username, "result": "Message successfully sent."}
                    else:
                        result = {"recipient": recipient_username, "result": "Not sent. Inbox limit reached."}
                    messages_stats.append(result)
                else:
                    continue
        else:
            error_message_over_255_characters = {
                "Character limit reached": "Message is too long (max. 255 characters)."
            }
            return error_message_over_255_characters
        return messages_stats

    def show_inbox(self, username):
        self.db.database_transaction(
            query="""UPDATE users_messages SET read_by_recipient = true WHERE recipient_username = %s;""",
            params=(username,))
        messages = self.db.database_transaction(
            query="""SELECT sender_username, message_content,sending_date
             FROM users_messages WHERE recipient_username = %s;""",
            params=(username,))
        print(messages)
        return messages

    def check_if_user_has_admin_privilege(self, username):
        result = self.db.database_transaction(
            query="""SELECT COUNT(*) FROM users_privileges WHERE username = %s AND privilege = %s;""",
            params=(username, "admin"))
        # output from result in format [(1,)] if user has admin privileges or [(0,)] if don't
        if result[0][0]:
            return True
        else:
            return False

    def count_unread_messages_in_username_inbox(self, username):
        result = self.db.database_transaction(
            query="""SELECT COUNT(*) FROM users_messages WHERE recipient_username = %s AND read_by_recipient = %s;""",
            params=(username, False))
        # output from result in format [(N,)] where N is numer of unread messages
        unread_messages = result[0][0]
        return unread_messages

    def get_all_users_list(self):

        result = self.db.database_transaction(
            query="""SELECT username FROM users_privileges;""")
        users_list = [user[0] for user in result]
        return users_list
