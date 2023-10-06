import unittest
from server_logic import Server
from user_logic import User
from client_logic import Client


class TestServerLogic(unittest.TestCase):

    def setUp(self):
        self.server = Server('192.168.0.163', 61033, 1024)

    def test_should_server_return_generated_password_with_correct_length(self):
        result = len(self.server.password_generator())
        self.assertEqual(result, 12)

    def test_should_server_return_generated_password_of_type_str(self):
        result = self.server.password_generator()
        self.assertIsInstance(result, str)

    def test_should_server_return_generated_password_with_at_least_8_random_symbols(self):
        result = len(set(self.server.password_generator()))
        self.assertGreaterEqual(result, 8)

    def test_add_user(self):
        result = self.server.add_user(username="test_user")
        self.assertIn("Success", result)

    def test_add_admin(self):
        result = self.server.add_user(username="test_user", privilege="admin")
        self.assertIn("Success", result)

    def test_should_server_dont_add_user_starts_with_no_alpha_symbol(self):
        result = self.server.add_user(username="1abc")
        self.assertEqual(result, 'The user have to start with a letter.')

    def test_should_server_dont_add_user_with_existed_username(self):
        self.server.add_user(username="Mario")
        result = self.server.add_user(username="Mario")
        self.assertEqual(result, 'The user with this name exists, choose another username.')

    def test_should_login_in_with_correct_data(self):
        self.server.add_user(username="Marek")
        new_user_username = self.server.users_with_passwords[0]['username']
        new_user_password = self.server.users_with_passwords[0]['password']
        result = self.server.login_into_system(new_user_username, new_user_password)
        self.assertTrue(result)

    def test_should_login_in_with_incorrect_data(self):
        new_user_username = "test_user"
        new_user_password = "test_password"
        result = self.server.login_into_system(new_user_username, new_user_password)
        self.assertFalse(result)

    def test_should_server_recognize_admin_privilege(self):
        self.server.add_user(username="test_admin", privilege="admin")
        result = self.server.check_if_admin(self.server.users[0])
        self.assertTrue(result)

    def test_should_server_recognize_if_no_admin_privilege_only_basic_user(self):
        self.server.add_user(username="test_admin", privilege="user")
        result = self.server.check_if_admin(self.server.users[0])
        self.assertFalse(result)

    def test_should_server_recognize_if_incorrect_privilege_given(self):
        self.server.add_user(username="test_admin", privilege="random_privilege")
        result = self.server.check_if_admin(self.server.users[0])
        self.assertFalse(result)

    def test_should_send_message_to_not_existed_recipient(self):
        self.server.add_user(username="user1")
        result = self.server.send_message(sender="user1", recipient_username="user2", message="test_message")
        self.assertEqual(result, "The recipient does not exist.")

    def test_should_send_message_with_over_255_symbols(self):
        self.server.add_user(username="user1")
        self.server.add_user(username="user2")
        result = self.server.send_message(sender="user1", recipient_username="user2",
                                          message="Lorem1_!" * 40)
        self.assertEqual(result, "Message is too long (max. 255 characters).")

    def test_should_send_message_with_over_255_only_numbers(self):
        self.server.add_user(username="user1")
        self.server.add_user(username="user2")
        result = self.server.send_message(sender="user1", recipient_username="user2",
                                          message="1" * 260)
        self.assertEqual(result, "Message is too long (max. 255 characters).")

    def test_should_send_message_successfully(self):
        self.server.add_user(username="user1")
        self.server.add_user(username="user2")
        sender = self.server.get_user_if_exists(username="user1")
        result = self.server.send_message(sender=sender, recipient_username="user2",
                                          message="test_message")
        self.assertEqual(result, "The message has been successfully sent.")

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
        self.assertEqual(result, "The recipient has reached the message limit in the inbox.")

    def test_should_empty_inbox_returned(self):
        self.server.add_user("user1")
        user = self.server.get_user_if_exists(username="user1")
        result = self.server.show_inbox(user)
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
