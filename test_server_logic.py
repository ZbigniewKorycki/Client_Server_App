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
        user1st = self.server.add_user(username="Mario")
        result = self.server.add_user(username="Mario")
        self.assertEqual(result, 'The user with this name exists, choose another username.')



if __name__ == '__main__':
    unittest.main()


