from datetime import datetime


class Server:
    def __init__(self, host, port, buffer, start_version="0.1.0"):
        self.host = host
        self.port = port
        self.buffer = buffer
        self.creation_time = datetime.now()
        self.versions = []
        self.add_server_version(start_version)

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

