import sys
import os.path
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from less0n import app, database
from less0n.models import *
from config import Auth


class MainTest(unittest.TestCase):
    """This class uses the Flask tests app to run an integration test against a
    local instance of the server."""

    def setUp(self):
        self.app = app.test_client()
        database.init_db()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_index(self):
        rv = self.app.get('/')
        data = rv.data.decode("utf-8")
        assert("Welcome to Less0n" in data)

    def test_login(self):
        rv = self.app.get('/login')
        assert(rv._status_code == 302)
        assert(Auth.AUTH_URI in rv.location)


if __name__ == '__main__':
    unittest.main()