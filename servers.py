import datetime

class Servers:
    def __init__(self, host, port, buffer):
        self.host = host
        self.port = port
        self.buffer = buffer
        self.creation_time = datetime.datetime.now()

    def get_uptime(self):
        current_time = datetime.datetime.now()
        server_uptime = current_time - self.creation_time
        return server_uptime
