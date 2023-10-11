from datetime import datetime
from user_logic import User
import random
import string
from db_connection import PostgresSQLConnection


class Server:
    def __init__(self, host, port, buffer, start_version="0.1.0"):
        self.host = host
        self.port = port
        self.buffer = buffer
        self.creation_time = datetime.now()
        self.versions = []
        self.add_server_version(start_version)
        self.users_with_passwords = []
        self.users = []
        self.versions_db = self.get_server_versions()

    def get_server_versions(self):
        db = PostgresSQLConnection()
        db.database_transaction(query="""CREATE TABLE IF NOT EXISTS server_versions (
                                            version VARCHAR(20) PRIMARY KEY,
                                            version_date TIMESTAMP);""")
        result = db.database_transaction(query="""SELECT * FROM server_versions;""")
        return result

    def get_server_uptime(self):
        current_time = datetime.now()
        server_uptime = current_time - self.creation_time
        return server_uptime

    def add_server_version(self, version_num):
        if version_num not in self.versions:
            new_version = {"version": version_num,
                           "version_date": datetime.now().strftime("%m/%d/%Y, %H:%M")}
            self.versions.append(new_version)
            return self.versions

    def add_user(self, username, privilege="user"):
        if self.get_user_if_exists(username):
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
            user = User(username, privilege=privilege)
            user_with_password = {"username": username,
                                  "password": self.password_generator()
                                  }
            self.users_with_passwords.append(user_with_password)
            self.users.append(user)
            # print(user_with_password)
            success_message = {
                "User added": f"'{username}' has been successfully added do userbase."
            }
            return success_message

    def password_generator(self):
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for i in range(12))
        return password

    def login_into_system(self, username, password):
        try:
            self.users_with_passwords.index({"username": username,
                                             "password": password
                                             })
        except ValueError:
            return False
        else:
            return True

    def get_user_if_exists(self, username):
        for user in self.users:
            if user.username == username:
                return user
        return False

    def user_base_interface(self, user):
        logged_user = user.username
        inbox_info = f"In your inbox you have: {user.unread_messages_in_inbox} unread messages."
        return logged_user, inbox_info

    def send_message(self, sender, recipient_username, message):
        if not self.get_user_if_exists(recipient_username):
            error_message_no_recipient = {
                "No recipient": "Recipient with given username don't exist."
            }
            return error_message_no_recipient
        else:
            recipient_user = self.get_user_if_exists(recipient_username)
            if len(message) <= 255:
                if (recipient_user.unread_messages_in_inbox < User.INBOX_UNREAD_MESSAGES_LIMIT_FOR_USER) or (
                        recipient_user.privilege == "admin"):
                    message_info = {"sender": sender.username, "recipient": recipient_username, "message": message,
                                    "date": datetime.now().strftime("%m/%d/%Y, %H:%M"), "status": "unread"}
                    recipient_user.inbox.insert(0, message_info)
                    recipient_user.unread_messages_in_inbox += 1
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

    def send_message_to_all(self, sender, message):
        messages_stats = []
        if len(message) <= 255:
            for user in self.users:
                if user != sender:
                    if (user.unread_messages_in_inbox < User.INBOX_UNREAD_MESSAGES_LIMIT_FOR_USER) or (
                            user.privilege == "admin"):
                        message_info = {"sender": sender.username, "recipient": user.username, "message": message,
                                        "date": datetime.now().strftime("%m/%d/%Y, %H:%M"), "status": "unread"}
                        user.inbox.insert(0, message_info)
                        user.unread_messages_in_inbox += 1
                        result = {"recipient": user.username, "result": "Message successfully sent."}
                    else:
                        result = {"recipient": user.username, "result": "Not sent. Inbox limit reached."}
                    messages_stats.append(result)
                else:
                    continue
        else:
            error_message_over_255_characters = {
                "Character limit reached": "Message is too long (max. 255 characters)."
            }
            return error_message_over_255_characters
        return messages_stats

    def show_inbox(self, user):
        for message in user.inbox:
            if message["status"] == "unread":
                message["status"] = "read"
        user.unread_messages_in_inbox = 0
        return user.inbox

    def check_if_admin(self, user):
        return user.privilege == "admin"
