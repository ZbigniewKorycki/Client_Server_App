
class User:


    def __init__(self, username, privilege="user"):
        self.username = username
        self.inbox = []
        self.unread_messages_in_inbox = 0
        self.privilege = privilege
