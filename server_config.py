from datetime import datetime
from user import User
import random
import string


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
        self.users_with_privileges = []

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

    def add_user(self, username):

        user_with_password = {"username": username,
                              "password": self.password_generator()
                              }
        user_with_privilege = {"username": username,
                               "privilege": "user"
                               }
        user = User(username)
        self.users_with_passwords.append(user_with_password)
        print(self.users_with_passwords)
        self.users.append(user)
        print(self.users)
        self.users_with_privileges.append(user_with_privilege)
        print(self.users_with_privileges)

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

    def get_user(self, username):
        for user in self.users:
            if user.username == username:
                return user
        return False

    def user_base_interface(self, user):
        logged_user = user.username
        inbox_info = f"In your inbox you have: {user.messages_in_inbox}/5 messages."
        commands_info = "'send': Send message to other user, 'inbox': Open your inbox, 'logout': Log out from account"
        return logged_user, inbox_info, commands_info

    def send_message(self, sender, recipient, message):
        if not self.get_user(recipient):
            return "The recipient does not exist."
        else:
            to_user = self.get_user(recipient)
            if len(message) <= 255:
                if to_user.messages_in_inbox < User.INBOX_MESSAGES_LIMIT_FOR_USER:
                    message_info = {"sender": sender.username, "recipient": recipient, "message": message,
                                    "date": datetime.now().strftime("%m/%d/%Y, %H:%M")}
                    to_user.inbox.append(message_info)
                    to_user.messages_in_inbox += 1
                    return "The message has been successfully sent."
                else:
                    return "The recipient has reached the message limit in the inbox."
            else:
                return "Message is too long (max. 255 characters)."


    def show_inbox(self, user):
        return user.inbox
