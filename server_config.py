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
        self.users_info = []
        self.users = []

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

    def add_user(self, username, privileges="user"):
        user_data = {"username": username,
                     "password": self.password_generator(),
                     "privileges": privileges}
        user = User(username)
        self.users_info.append(user_data)
        print(self.users_info)
        self.users.append(user)
        print(self.users)

    def password_generator(self):
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for i in range(12))
        print(password)
        return password
