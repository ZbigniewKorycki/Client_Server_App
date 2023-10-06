import unittest
from server_logic import Server


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

    def test_should_server_add_user_with_correct_name(self):
        result = self.server.add_user(username="Mario")
        self.assertEqual(result, 'The new user: Mario has been successfully added.')

    def test_should_server_dont_add_user_starts_with_no_alpha_symbol(self):
        result = self.server.add_user(username="1abc")
        self.assertEqual(result, 'The user have to start with a letter.')

    def test_should_server_dont_add_user_with_existed_username(self):
        user_first = self.server.add_user(username="Mario")
        user_duplicate = self.server.add_user(username="Mario")
        self.assertEqual(user_duplicate, 'The user with this name exists, choose another username.')

    def test_should_login_in_with_correct_data(self):
        new_user = self.server.add_user(username="Marek")
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
        new_admin = self.server.add_user(username="test_admin", privilege="admin")
        result = self.server.check_if_admin(self.server.users[0])
        self.assertTrue(result)

    def test_should_server_recognize_if_no_admin_privilege_only_basic_user(self):
        new_admin = self.server.add_user(username="test_admin", privilege="user")
        result = self.server.check_if_admin(self.server.users[0])
        self.assertFalse(result)

    def test_should_server_recognize_if_incorrect_privilege_given(self):
        new_admin = self.server.add_user(username="test_admin", privilege="random_privilege")
        result = self.server.check_if_admin(self.server.users[0])
        self.assertFalse(result)

    def test_should_send_message_to_not_existed_recipient(self):
        user_sender = self.server.add_user(username="user1")
        result = self.server.send_message(sender="user1", recipient="user2", message="test_message")
        self.assertEqual(result, "The recipient does not exist.")

    def test_should_send_message_with_over_255_symbols(self):
        user_sender = self.server.add_user(username="user1")
        user_recipient = self.server.add_user(username="user2")
        result = self.server.send_message(sender="user1", recipient="user2",
                                          message="Lorem Ipsum is simply dummy text of the printing and"
                                                  " typesetting industry. Lorem Ipsum has been the industry's"
                                                  " standard dummy text ever since the 1500s, when an unknown"
                                                  " printer took a galley of type and scrambled it to make"
                                                  " a type specimen book. It has survived not only five centuries,"
                                                  " but also the leap into electronic typesetting,"
                                                  " remaining essentially unchanged."
                                                  " It was popularised in the 1960s with the release of"
                                                  " Letraset sheets containing Lorem Ipsum passages, and more"
                                                  " recently with desktop publishing software like"
                                                  " Aldus PageMaker including versions of Lorem Ipsum.")
        self.assertEqual(result, "Message is too long (max. 255 characters).")


if __name__ == '__main__':
    unittest.main()
