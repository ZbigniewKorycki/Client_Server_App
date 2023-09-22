class User:

    def __init__(self, username):
        self.username = username
        self.inbox = []
        self.messages_in_inbox = len(self.inbox)
