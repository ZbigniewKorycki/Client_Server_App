import unittest
from server_config import Server

class TestServer(unittest.TestCase):

    def setUp(self):
        self.server = Server('192.168.0.163', 61033, 1024)

    def test_should_server_return_generated_password(self):
        result = self.server.password_generator()
        self.assertEqual(len(result), 12)


if __name__ == '__main__':
    unittest.main()


