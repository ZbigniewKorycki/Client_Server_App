import unittest
from server_logic import Server
from user_logic import User
from client_logic import Client


class TestServerLogic(unittest.TestCase):

    def setUp(self):
        self.server = Server('192.168.0.163', 61033, 1024)

    def test_return_generated_password_with_correct_length(self):
        result = len(self.server.password_generator())
        self.assertEqual(result, 12)

    def test_return_generated_password_of_type_str(self):
        result = self.server.password_generator()
        self.assertIsInstance(result, str)

    def test_return_generated_password_with_at_least_8_random_symbols(self):
        result = len(set(self.server.password_generator()))
        self.assertGreaterEqual(result, 8)

    def test_add_user(self):
        result = self.server.add_user(username="test_user")
        self.assertIn("User added", result)

    def test_add_admin(self):
        result = self.server.add_user(username="test_user", privilege="admin")
        self.assertIn("User added", result)

    def test_dont_add_username_starts_with_no_alpha_symbol(self):
        result = self.server.add_user(username="1abc")
        result1 = self.server.add_user(username="132455465")
        self.assertIn("Incorrect username", result)
        self.assertIn("Incorrect username", result1)

    def test_dont_add_empty_username(self):
        result = self.server.add_user(username="")
        self.assertIn("Empty username", result)

    def test_dont_add_username_with_space(self):
        result = self.server.add_user(username="test   user")
        result1 = self.server.add_user(username="testuser      ")
        self.assertIn("No space in username allowed", result)
        self.assertIn("No space in username allowed", result1)

    def test_dont_add_user_with_existed_username(self):
        self.server.add_user(username="test_user")
        result = self.server.add_user(username="test_user")
        self.assertIn("User duplicate", result)

    def test_login_in(self):
        self.server.add_user(username="user")
        user_password = self.server.users_with_passwords[0]['password']
        incorrect_user_username = "test_user"
        incorrect_user_password = "test_password"
        result_correct_user_and_password = self.server.login_into_system("user", user_password)
        result_incorrect_user_correct_password = self.server.login_into_system(incorrect_user_username, user_password)
        result_correct_user_incorrect_password = self.server.login_into_system("user", incorrect_user_password)
        self.assertTrue(result_correct_user_and_password)
        self.assertFalse(result_incorrect_user_correct_password)
        self.assertFalse(result_correct_user_incorrect_password)

    def test_recognize_admin_privilege(self):
        self.server.add_user(username="test_admin", privilege="admin")
        self.server.add_user(username="test_admin_1", privilege="user")
        self.server.add_user(username="test_admin_2", privilege="random_privilege")
        result_admin_privilege = self.server.check_if_admin(self.server.get_user_if_exists("test_admin"))
        result_user_privilege = self.server.check_if_admin(self.server.get_user_if_exists("test_admin_1"))
        result_unknown_privilege = self.server.check_if_admin(self.server.get_user_if_exists("test_admin_2"))
        self.assertTrue(result_admin_privilege)
        self.assertFalse(result_user_privilege)
        self.assertFalse(result_unknown_privilege)

    def test_send_message(self):
        self.server.add_user(username="user1")
        self.server.add_user(username="user2")
        sender = self.server.get_user_if_exists(username="user1")
        result_recipient_unknown = self.server.send_message(sender=sender, recipient_username="user_unknown",
                                                            message="test_message")
        result_success = self.server.send_message(sender=sender, recipient_username="user2",
                                                  message="test_message")
        result_over_255 = self.server.send_message(sender=sender, recipient_username="user2",
                                                   message="L" * 256)
        self.assertIn("No recipient", result_recipient_unknown)
        self.assertIn("Message sent", result_success)
        self.assertIn("Character limit reached", result_over_255)

    def test_should_not_find_non_existed_user(self):
        result = self.server.get_user_if_exists(username="test_user")
        self.assertFalse(result)

    def test_should_find_existed_user(self):
        self.server.add_user(username="test_user")
        user_obj = self.server.get_user_if_exists(username="test_user")
        self.assertIsInstance(user_obj, User)

    def test_should_recipient_inbox_increase_of_1_after_getting_message(self):
        self.server.add_user("user1")
        self.server.add_user("user2")
        sender = self.server.get_user_if_exists(username="user1")
        self.server.send_message(sender=sender, recipient_username="user2", message="test_message")
        recipient = self.server.get_user_if_exists(username="user2")
        messages_in_recipient_inbox = recipient.unread_messages_in_inbox
        self.assertEqual(messages_in_recipient_inbox, 1)

    def test_should_user_recipient_have_only_5_unread_messages(self):
        self.server.add_user("user1")
        self.server.add_user("user2")
        sender = self.server.get_user_if_exists(username="user1")
        for _ in range(User.INBOX_UNREAD_MESSAGES_LIMIT_FOR_USER * 3):
            self.server.send_message(sender=sender, recipient_username="user2", message="test_message")
        recipient = self.server.get_user_if_exists(username="user2")
        unread_messages = recipient.unread_messages_in_inbox
        self.assertEqual(unread_messages, User.INBOX_UNREAD_MESSAGES_LIMIT_FOR_USER)

    def test_should_admin_recipient_have_only_more_than_5_unread_messages(self):
        self.server.add_user("user1")
        self.server.add_user("user2", privilege="admin")
        sender = self.server.get_user_if_exists(username="user1")
        for _ in range(User.INBOX_UNREAD_MESSAGES_LIMIT_FOR_USER * 4):
            self.server.send_message(sender=sender, recipient_username="user2", message="test_message")
        recipient = self.server.get_user_if_exists(username="user2")
        unread_messages = recipient.unread_messages_in_inbox
        self.assertEqual(unread_messages, User.INBOX_UNREAD_MESSAGES_LIMIT_FOR_USER * 4)

    def test_should_sender_gets_info_when_recipient_has_full_inbox(self):
        self.server.add_user("user1")
        self.server.add_user("user2")
        sender = self.server.get_user_if_exists(username="user1")
        for _ in range(User.INBOX_UNREAD_MESSAGES_LIMIT_FOR_USER):
            self.server.send_message(sender=sender, recipient_username="user2", message="test_message")
        result = self.server.send_message(sender=sender, recipient_username="user2", message="test_message")
        self.assertIn("Inbox limit", result)

    def test_should_empty_inbox_returned(self):
        self.server.add_user("user1")
        user = self.server.get_user_if_exists(username="user1")
        result = self.server.show_inbox(user)
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
