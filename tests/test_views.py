import sys
import os.path
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import less0n


class MainTest(unittest.TestCase):
    """This class uses the Flask tests app to run an integration test against a
    local instance of the server."""

    def setUp(self):
        self.app = less0n.app.test_client()

    def test_hello_world(self):
        rv = self.app.get('/')
        data = rv.data.decode("utf-8")
        print(data)
        assert("hello" in data.lower())


if __name__ == '__main__':
    unittest.main()
