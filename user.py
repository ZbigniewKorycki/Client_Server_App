
class User:

    INBOX_UNREAD_MESSAGES_LIMIT_FOR_USER = 5

    def __init__(self, username):
        self.username = username
        self.inbox = []
        self.unread_messages_in_inbox = 0
