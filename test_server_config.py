import unittest
from server_config import Server

class TestServer(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()


