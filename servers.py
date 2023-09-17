from datetime import datetime


class Servers:
    def __init__(self, host, port, buffer):
        self.host = host
        self.port = port
        self.buffer = buffer
        self.creation_time = datetime.now()
        self.versions = []

    def get_server_uptime(self):
        current_time = datetime.now()
        server_uptime = current_time - self.creation_time
        return server_uptime

    def add_server_version(self, version_num):
        new_version = {"version": version_num,
                       "version_date": datetime.now().strftime("%m/%d/%Y, %H:%M")}
        self.versions.append(new_version)
        return self.versions
