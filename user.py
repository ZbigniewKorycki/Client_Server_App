class User:

    def __init__(self, username):
        self.username = username
        self.messages_in_inbox = 0
        self.address = f'@{username}'

