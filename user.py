
class User:

    INBOX_MESSAGES_LIMIT_FOR_USER = 2

    def __init__(self, username):
        self.username = username
        self.inbox = []
        self.messages_in_inbox = 0
