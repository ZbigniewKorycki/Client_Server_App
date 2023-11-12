from datetime import datetime
import random
import string
from db_connection_sqlite import SQLiteConnection


class Server:
    INBOX_UNREAD_MESSAGES_LIMIT_FOR_USER = 5

    def __init__(self, host, port, start_version="0.1.0", db=SQLiteConnection("pythonsqlite.db")):
        self.host = host
        self.port = port
        self.buffer = 1024
        self.db = db
        self.creation_time = datetime.now()
        self.add_server_version(start_version)
        self.generate_admin_token(num_of_tokens=5)

    def get_server_versions(self):
        versions = self.db.get_all(query="""SELECT * FROM server_versions;""", params=())
        return versions

    def add_server_version(self, version_num):
        version_num_occurrence = self.db.get_all(
            f"""SELECT COUNT(*) FROM server_versions WHERE version = ?""", params=(version_num, ))
        if version_num_occurrence[0][0] == 0:
            self.db.execute_query("""INSERT INTO server_versions VALUES (?, ?)""", (version_num, datetime.now().strftime("%d/%m/%Y, %H:%M")))
            return {f"Success": f"New server version: {version_num}, has been added."}
        else:
            return {f"Duplicate": f"Server version: {version_num}, already exists."}

    def delete_server_version(self, version_to_delete):
        version_num_occurrence = self.db.get_all(
            query="""SELECT COUNT(*) FROM server_versions WHERE version = ?;""",
            params=(version_to_delete,))
        if version_num_occurrence[0][0] == 0:
            return {f"Version doesn't exist": f"Server doesn't have version '{version_to_delete}.'"}
        else:
            self.db.execute_query(
                query="""DELETE FROM server_versions WHERE version = ?;""",
                params=(version_to_delete,))
            return {f"Version deleted": f"Server version '{version_to_delete}' successfully deleted."}

    def get_server_uptime(self):
        current_time = datetime.now()
        server_uptime = current_time - self.creation_time
        return server_uptime

    def add_user(self, username, privileges="user"):
        if self.check_if_username_exists(username):
            error_message_user_duplicate = {
                "User duplicate": f"The user '{username}' with this name exists already, choose another username."
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
            if privileges != "admin":
                privileges = "user"
            password = self.password_generator()
            self.db.execute_query(query="""INSERT INTO users (username) VALUES (?);""",
                                         params=(username,))
            self.db.execute_query(query="""INSERT INTO users_passwords VALUES (?, ?);""",
                                         params=(username, password))
            self.db.execute_query(query="""INSERT INTO users_privileges VALUES (?, ?);""",
                                         params=(username, privileges))
            print(password)
            success_message = {
                "User added": f"'{username}' has been successfully added do database."
            }
            return success_message

    def delete_user(self, username_to_delete):
        if not self.check_if_username_exists(username_to_delete):
            error_message_user_doesnt_exists = {
                "User doesn't exists": f"The user '{username_to_delete}' doesn't exists."
            }
            return error_message_user_doesnt_exists
        elif self.check_if_user_has_admin_privileges(username_to_delete):
            error_message_cant_delete_admin = {
                "User with admin privileges":
                    f"The user '{username_to_delete}' has admin privileges, you can't delete him."
            }
            return error_message_cant_delete_admin
        else:
            self.db.execute_query(
                query="""DELETE FROM users WHERE username = ?;""",
                params=(username_to_delete,))
            self.db.execute_query(
                query="""DELETE FROM users_privileges WHERE username = ?;""",
                params=(username_to_delete,))
            success_message_user_deleted = {"User deleted": f"All '{username_to_delete}' user data has been deleted."}
            return success_message_user_deleted

    def password_generator(self, length=12):
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for _ in range(length))
        return password

    def login_into_system(self, username, password):
        result = self.db.get_all(
            query="""SELECT COUNT(*) FROM users_passwords WHERE username = ? AND password = ?;""",
            params=(username, password, ))
        if result[0][0] == 1:
            return True
        else:
            return False

    def check_if_username_exists(self, username):
        result = self.db.get_all(
            query="""SELECT COUNT(*) FROM users_privileges WHERE username = ?;""",
            params=(username,))
        # output from result in format [(1,)] if username exists or [(0,)] if not exists
        if result[0][0]:
            return True
        else:
            return False

    def user_base_interface(self, username):
        inbox_info = f"In your inbox you have: {self.count_unread_messages_in_user_inbox(username)} unread messages."
        return inbox_info

    def send_message(self, sender_username, recipient_username, message):
        if not self.check_if_username_exists(recipient_username):
            error_message_no_recipient = {
                "No recipient": "Recipient with given username don't exist."
            }
            return error_message_no_recipient
        else:
            if len(message) <= 255:
                if (self.count_unread_messages_in_user_inbox(
                        recipient_username) < self.INBOX_UNREAD_MESSAGES_LIMIT_FOR_USER) or (
                        self.check_if_user_has_admin_privileges(recipient_username)):
                    self.db.execute_query(
                        query="""INSERT INTO users_messages(sender_username,
                                    recipient_username,
                                    message_content,
                                    sending_date)
                                    VALUES (?, ?, ?, ?);""",
                        params=(sender_username,
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
                    if (self.count_unread_messages_in_user_inbox(
                            recipient_username) < self.INBOX_UNREAD_MESSAGES_LIMIT_FOR_USER) or (
                            self.check_if_user_has_admin_privileges(recipient_username)):
                        self.db.execute_query(
                            query="""INSERT INTO users_messages(sender_username,
                                                                recipient_username,
                                                                message_content,
                                                                sending_date)
                                                                VALUES (?, ?, ?, ?);""",
                            params=(sender_username,
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
        self.db.execute_query(
            query="""UPDATE users_messages SET read_by_recipient = 1 WHERE recipient_username = ?;""",
            params=(username,))
        messages = self.db.get_all(
            query="""SELECT sender_username, message_content,sending_date
             FROM users_messages WHERE recipient_username = ? ORDER BY sending_date DESC;""",
            params=(username,))

        return messages

    def check_if_user_has_admin_privileges(self, username):
        result = self.db.get_all(
            query="""SELECT COUNT(*) FROM users_privileges WHERE username = ? AND privileges = ?;""",
            params=(username, "admin"))
        # output from result in format [(1,)] if user has admin privileges or [(0,)] if only user privileges
        if result[0][0]:
            return True
        else:
            return False

    def change_user_privileges(self, username, new_privileges):
        if not self.check_if_username_exists(username):
            error_message_user_doesnt_exists = {
                "User doesn't exists": f"The user '{username}' doesn't exists."
            }
            return error_message_user_doesnt_exists
        elif new_privileges not in ['admin', 'user']:
            error_message_incorrect_privileges = {
                "Incorrect privileges": f"Given privileges '{new_privileges}' are not valid."
            }
            return error_message_incorrect_privileges
        else:
            self.db.execute_query(query="""UPDATE users_privileges SET privileges = ? WHERE username = ?;""",
                                         params=(new_privileges, username,))
            message_privileges_changed = \
                {"Privileges changed": f"The user '{username}' now has an {new_privileges} privileges."}
            return message_privileges_changed

    def count_unread_messages_in_user_inbox(self, username):
        result = self.db.get_all(
            query="""SELECT COUNT(*) FROM users_messages WHERE recipient_username = ? AND read_by_recipient = ?;""",
            params=(username, 0))
        # output from result in format [(N,)] where N is numer of unread messages
        unread_messages = result[0][0]
        return unread_messages

    def get_all_users_list(self):
        result = self.db.get_all(
            query="""SELECT username FROM users_privileges WHERE privileges = ?;""", params=("user", ))
        users_list = [user[0] for user in result]
        print(users_list)
        return users_list

    def get_table_column_names(self, table_name):
        result = self.db.get_all(
            query="""SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = ?;""",
            params=(table_name,))
        # output from result in format [('column_name1',), ('column_name2',)]
        column_names = [column[0] for column in result]
        print(column_names)

    def generate_admin_token(self, num_of_tokens):
        for _ in range(num_of_tokens):
            admin_token = self.password_generator(length=60)
            self.db.execute_query(query="""INSERT INTO admin_tokens VALUES (?, ?);""", params=(admin_token, 1, ))

    def verify_admin_token(self, admin_token_to_check):
        result = self.db.get_all(
            query="""SELECT COUNT(*) FROM admin_tokens WHERE token_id = ? and is_valid = ?;""",
            params=(admin_token_to_check, 1,))
        if result[0][0] == 1:
            self.db.execute_query(
                query="""UPDATE admin_tokens set is_valid = ? WHERE token_id = ?;""",
                params=(0, admin_token_to_check,))
            return True
        else:
            return False
