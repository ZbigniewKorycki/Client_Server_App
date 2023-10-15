import unittest
from server_logic import Server
import datetime
import commands
from db_connection import PostgresSQLConnection


class TestServerLogic(unittest.TestCase):

    def setUp(self):
        self.server = Server('192.168.0.163', 61033, db=PostgresSQLConnection("test_db"))

    def test_server_uptime(self):
        result = self.server.get_server_uptime()
        self.assertIsInstance(result, datetime.timedelta)

    def test_add_delete_server_version(self):
        self.server.add_server_version("1.2.6")
        result_all_versions_after_adding = [version[0] for version in self.server.get_server_versions()]
        self.assertIn("1.2.6", result_all_versions_after_adding)
        self.server.delete_server_version("1.2.6")
        result_all_versions_after_deletion = [version[0] for version in self.server.get_server_versions()]
        self.assertNotIn("1.2.6", result_all_versions_after_deletion)

    def test_generated_password(self):
        password = self.server.password_generator()
        password_len = len(password)
        password_len_various_symbols = len(set(password))
        self.assertEqual(password_len, 12)
        self.assertIsInstance(password, str)
        self.assertGreaterEqual(password_len_various_symbols, 8)

    def test_add_delete_user(self):
        result_adding = self.server.add_user(username="test_user_123")
        result_if_admin = self.server.check_if_user_has_admin_privileges("test_user_123")
        self.assertIn("User added", result_adding)
        self.assertFalse(result_if_admin)
        result_after_deletion = self.server.delete_user(username_to_delete="test_user_123")
        self.assertIn("User deleted", result_after_deletion)
        self.assertFalse(self.server.check_if_username_exists(username="test_user123"))

    def test_add_delete_admin(self):
        result_adding_admin = self.server.add_user(username="test_admin", privileges="admin")
        self.assertIn("User added", result_adding_admin)
        result_if_admin = self.server.check_if_user_has_admin_privileges(username="test_admin")
        self.assertTrue(result_if_admin)
        result_change_privileges_to_user = self.server.change_user_privileges("test_admin", "user")
        self.assertIn("Privileges changed", result_change_privileges_to_user)
        result_if_admin_after_change = self.server.check_if_user_has_admin_privileges(username="test_admin")
        self.assertFalse(result_if_admin_after_change)
        result_delete_user = self.server.delete_user("test_admin")
        self.assertIn("User deleted", result_delete_user)

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
        result1 = self.server.add_user(username="test_user      ")
        self.assertIn("No space in username allowed", result)
        self.assertIn("No space in username allowed", result1)

    def test_dont_add_user_with_existed_username(self):
        self.server.add_user(username="test_user123")
        result_after_adding_duplicate = self.server.add_user(username="test_user123")
        self.assertIn("User duplicate", result_after_adding_duplicate)
        result_after_deletion = self.server.delete_user(username_to_delete="test_user123")
        self.assertIn("User deleted", result_after_deletion)
        self.assertFalse(self.server.check_if_username_exists(username="test_user123"))

    def test_login_in(self):
        self.server.add_user(username="user_test123")
        password = self.server.db.database_transaction(
            query="""SELECT password FROM users_passwords WHERE username = %s;""",
            params=("user_test123",))[0]
        incorrect_user_username = "test_user"
        incorrect_user_password = "test_password"
        result_correct_user_and_password = self.server.login_into_system("user_test123", password)
        result_incorrect_user_correct_password = self.server.login_into_system(incorrect_user_username, password)
        result_correct_user_incorrect_password = self.server.login_into_system("user_test123", incorrect_user_password)
        self.assertTrue(result_correct_user_and_password)
        self.assertFalse(result_incorrect_user_correct_password)
        self.assertFalse(result_correct_user_incorrect_password)
        self.server.delete_user("user_test123")

    def test_recognize_admin_privileges(self):
        self.server.add_user(username="test_admin", privileges="admin")
        self.server.add_user(username="test_admin_1", privileges="user")
        self.server.add_user(username="test_admin_2", privileges="random_privileges")
        result_if_admin_admin_privileges = self.server.check_if_user_has_admin_privileges("test_admin")
        result_if_admin_user_privileges = self.server.check_if_user_has_admin_privileges("test_admin_1")
        result_if_admin_unknown_privileges = self.server.check_if_user_has_admin_privileges("test_admin_2")
        self.assertTrue(result_if_admin_admin_privileges)
        self.assertFalse(result_if_admin_user_privileges)
        self.assertFalse(result_if_admin_unknown_privileges)
        self.server.change_user_privileges("test_admin", "user")
        self.server.delete_user("test_admin")
        self.server.delete_user("test_admin_1")
        self.server.delete_user("test_admin_2")

    def test_send_message(self):
        self.server.add_user(username="user1")
        self.server.add_user(username="user2")
        result_recipient_unknown = self.server.send_message(sender_username="user1",
                                                            recipient_username="user_unknown",
                                                            message="test message")
        result_correct_data = self.server.send_message(sender_username="user1",
                                                       recipient_username="user2",
                                                       message="test message")
        result_over_255_characters = self.server.send_message(sender_username="user1",
                                                              recipient_username="user2",
                                                              message="M" * 256)
        self.assertIn("No recipient", result_recipient_unknown)
        self.assertIn("Message sent", result_correct_data)
        self.assertIn("Character limit reached", result_over_255_characters)
        self.server.delete_user("user1")
        self.server.delete_user("user2")

    def test_should_find_existed_user(self):
        self.server.add_user(username="test_user")
        result_user = self.server.check_if_username_exists(username="test_user")
        result_user_incorrect = self.server.check_if_username_exists(username="random_user")
        self.assertTrue(result_user)
        self.assertFalse(result_user_incorrect)
        self.server.delete_user("test_user")

    def test_recipient_inbox_admin_privileges(self):
        self.server.add_user("user1")
        self.server.add_user("user-admin", privileges="admin")
        for _ in range(self.server.INBOX_UNREAD_MESSAGES_LIMIT_FOR_USER):
            self.server.send_message(sender_username="user1", recipient_username="user-admin", message="test_message")
        result_message_over_limit = self.server.send_message(sender_username="user1", recipient_username="user-admin",
                                                             message="test_message")
        self.assertIn("Message sent", result_message_over_limit)
        messages_in_admin_inbox = self.server.count_unread_messages_in_user_inbox("user-admin")
        self.assertEqual(messages_in_admin_inbox, self.server.INBOX_UNREAD_MESSAGES_LIMIT_FOR_USER + 1)
        self.server.change_user_privileges("user-admin", "user")
        self.server.delete_user("user1")
        self.server.delete_user("user-admin")

    def test_should_sender_gets_info_when_recipient_has_full_inbox(self):
        self.server.add_user("user1")
        self.server.add_user("user2")
        for x in range(self.server.INBOX_UNREAD_MESSAGES_LIMIT_FOR_USER):
            self.server.send_message(sender_username="user1",
                                     recipient_username="user2",
                                     message="test_message")
        result_message_over_limit = self.server.send_message(sender_username="user1",
                                                             recipient_username="user2",
                                                             message="test_message")
        unread_messages_in_recipient_inbox = self.server.count_unread_messages_in_user_inbox("user2")
        self.assertIn("Inbox limit", result_message_over_limit)
        self.assertEqual(unread_messages_in_recipient_inbox, self.server.INBOX_UNREAD_MESSAGES_LIMIT_FOR_USER)
        self.server.delete_user("user1")
        self.server.delete_user("user2")

    def test_send_message_to_all_users(self):
        self.server.add_user("user-admin", privileges="admin")
        for x in range(5):
            self.server.add_user(f"user{x}")
        result = self.server.send_message_to_all("user-admin", "test message")
        self.assertEqual(len(result), 5)
        self.assertIn("recipient", result[0])
        self.assertIn("result", result[0])
        for x in range(5):
            self.server.delete_user(f"user{x}")
        self.server.change_user_privileges("user-admin", "user")
        self.server.delete_user("user-admin")

    def test_send_message_to_all_users_over_255_characters(self):
        self.server.add_user("user-admin", privileges="admin")
        for x in range(5):
            self.server.add_user(f"user{x}")
        result = self.server.send_message_to_all(sender_username="user-admin", message="M" * 256)
        self.assertIn("Character limit reached", result)
        for x in range(5):
            self.server.delete_user(f"user{x}")
        self.server.change_user_privileges("user-admin", "user")
        self.server.delete_user("user-admin")

    def test_should_empty_inbox_returned(self):
        self.server.add_user("user1")
        result = self.server.show_inbox("user1")
        self.assertEqual(result, [])
        self.server.delete_user("user1")

    def test_should_inbox_shown_with_messages(self):
        self.server.add_user("user1")
        self.server.add_user("user2")
        self.server.add_user("user3")
        self.server.send_message("user1", "user3", "test message from user1")

        self.server.send_message("user2", "user3", "test message from user2")
        result_latest_message = self.server.show_inbox("user3")[-1]
        result_oldest_message = self.server.show_inbox("user3")[0]
        self.assertIn("user2", result_latest_message)
        self.assertIn("test message from user2", result_latest_message)
        self.assertIn("user1", result_oldest_message)
        self.assertIn("test message from user1", result_oldest_message)
        self.server.delete_user("user1")
        self.server.delete_user("user2")
        self.server.delete_user("user3")

    def test_show_user_base_interface(self):
        self.server.add_user("user9")
        inbox_info = self.server.user_base_interface("user9")
        self.assertIn("0 unread messages", inbox_info)
        self.assertTrue(self.server.check_if_username_exists("user9"))
        self.server.delete_user("user9")

    def test_get_all_users_list(self):
        self.server.add_user("John")
        self.server.add_user("Peter")
        self.server.add_user("Adam")
        user_list = self.server.get_all_users_list()
        self.assertEqual(len(user_list), 3)
        self.assertIn("John", user_list)
        self.assertIn("Peter", user_list)
        self.assertIn("Adam", user_list)
        self.server.delete_user("John")
        self.server.delete_user("Peter")
        self.server.delete_user("Adam")



class TestCommandsDescription(unittest.TestCase):

    def test_commands_description(self):
        result = commands.commands_description
        self.assertIn("add-admin", result)
        self.assertIn("add-user", result)
        self.assertIn("help", result)
        self.assertIn("inbox", result)
        self.assertIn("info", result)
        self.assertIn("login", result)
        self.assertIn("send", result)
        self.assertIn("send-to-all", result)
        self.assertIn("stop", result)
        self.assertIn("uptime", result)
        self.assertIn("add-server-version", result)
        self.assertIn("delete-user", result)
        self.assertIn("change-privileges", result)


if __name__ == '__main__':
    unittest.main()
