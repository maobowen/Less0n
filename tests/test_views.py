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
        database.drop_db()

    def test_index(self):
        rv = self.app.get('/')
        data = rv.data.decode("utf-8")
        assert("Welcome to Less0n" in data)

    def test_login(self):
        rv = self.app.get('/login')
        assert(rv._status_code == 302)
        assert(Auth.AUTH_URI in rv.location)

    def test_department_course_with_valid_arg(self):
        """
        Test if department_course() return department-course.html with valid department name
        Test cases:
        --------------------------------------------------
        Input                             Expected Output
        /dept/COMS/                       COMS in html
        """
        rv = self.app.get('/dept/COMS/')
        assert rv._status_code == 200
        assert rv.content_type == 'text/html; charset=utf-8'
        data = rv.data.decode('utf-8').lower() # convert data to lower case
        assert 'department-course' in data
        assert 'coms' in data

    def test_department_course_with_unvalid_arg(self):
        """
        Test if department_course() return department-course.html with unvalid department name
        Test cases:
        --------------------------------------------------
        Input                             Expected Output
        /dept/AAAA/                       302, department in html
        """
        rv = self.app.get('/dept/AAAA/')
        assert rv._status_code == 302
        assert rv.content_type == 'text/html; charset=utf-8'
        data = rv.data.decode('utf-8').lower() # convert data to lower case
        assert 'department' in data

    def test_course_with_valid_arg(self):
        """
        Test if course() return course-detail.html with valid argument
        Test case:
        --------------------------------------------------
        Input                             Expected Output
        /course/COMS3157/                       department in html
        """
        rv = self.app.get('/course/COMS3157/')
        assert rv._status_code == 200
        assert rv.content_type == 'text/html; charset=utf-8'
        data = rv.data.decode('utf-8').lower()  # convert data to lower case
        assert 'course-detail' in data
        assert 'coms3157' in data


    def test_course_with_unvalid_arg(self):
        """
        Test if course() return course-detail.html with valid argument
        Test case:
        --------------------------------------------------
        Input                             Expected Output
        /course/COMS2222/                 department in html
        /course/ABCDEFG/                  404
        """
        rv = self.app.get('/course/COMS2222/')
        assert rv._status_code == 302
        assert rv.content_type == 'text/html; charset=utf-8'
        data = rv.data.decode('utf-8').lower()  # convert data to lower case
        assert 'department' in data

        rv = self.app.get('/course/ABCDEFG/')
        assert rv._status_code == 404

    def test_course_json_with_valid_arg(self):
        """
        Test if course() return course-detail.html with valid argument
        Test case:
        --------------------------------------------------
        Input                             Expected Output
        /course/COMS3157/json             JSON data
        """
        rv = self.app.get('/course/COMS3157/json/')
        assert rv._status_code == 200
        assert rv.content_type == 'application/json'

    def test_course_json_with_unvalid_arg(self):
        """
        Test if course() return course-detail.html with valid argument
        Test case:
        --------------------------------------------------
        Input                             Expected Output
        /course/COMS1234/json             empty JSON data
        /course/ABCDEFG/json              404
        """
        rv = self.app.get('/course/COMS1234/json/')
        assert rv._status_code == 200
        assert rv.content_type == 'application/json'
        assert rv.data.decode('utf-8') == '[]\n'

        rv = self.app.get('/course/ABCDEFG/json/')
        assert rv._status_code == 404


if __name__ == '__main__':
    unittest.main()
