import sys
import os.path
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from less0n import app, database
from less0n.models import *
from config import Auth
import re
# import flask_testing
# from flask import Flask


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

    def test_department(self):
        """
        Test if department() with GET return rendered department.html
        """
        rv = self.app.get('/department')
        assert rv._status_code == 200
        assert rv.content_type == 'text/html; charset=utf-8'
        assert 'department' in rv.data.decode('utf-8').lower() # "department.html" must have Department

    def testDepartmentSearchWithValidInput(self):
        """
        Test if department() with POST return department.html with correct department name

        Test cases:
        --------------------------------------------------
        dept_keyword Input                Expected Output
        computer                          computer in html
        """
        rv = self.app.post('/department', data = dict(
            dept_keyword = "computer"
        ))
        assert rv._status_code == 200
        assert rv.content_type == 'text/html; charset=utf-8'
        data = rv.data.decode('utf-8').lower() # convert data to lower case
        assert 'department' in data
        # assert 'computer' in data

    def testDepartmentSearchWithUnvalidInput(self):
        """
        Test if department() with POST return department.html with correct department name

        Test cases:
        --------------------------------------------------
        dept_keyword Input                Expected Output
        zhongwenxi                        No word between <section id="sort-alphabetical" data-filter-group="dept"> and </section>
        """
        rv = self.app.post('/department', data = dict(
            dept_keyword = "zhongwenxi"
        ))
        assert rv._status_code == 200
        assert rv.content_type == 'text/html; charset=utf-8'
        data = rv.data.decode('utf-8').lower() # convert data to lower case
        assert 'department' in data

        # search <div class="row" id="alphabetical-card"> \n \n .. </div>
        pattern = re.compile('<div class="row" id="alphabetical-card">(\s*\n\s*)+</div>')
        assert pattern.search(data) is not None

    def testDepartmentSearchWithEmptyInput(self):
        """
        Test if department() with POST return department.html with correct department name

        Test cases:
        --------------------------------------------------
        dept_keyword Input                Expected Output
        empty string                      'computer science' in department.html
        """
        rv = self.app.post('/department', data=dict(
            dept_keyword=""
        ))
        assert rv._status_code == 200
        assert rv.content_type == 'text/html; charset=utf-8'
        data = rv.data.decode('utf-8').lower()  # convert data to lower case
        assert 'department' in data
        assert 'computer science' in data


# class TemplateTest(flask_testing.TestCase):
#     """
#     This class is to test rendered template using Flask-Testing package
#     """
#
#     def create_app(self):
#         # app = Flask(__name__)
#         app.config['TESTING'] = True
#         return app
#
#     def setUp(self):
#         # self.app = app.test_client()
#         database.init_db()
#
#     def tearDown(self):
#         database.drop_db()
#
#     def test_department(self):
#         with self.app.test_client() as client:
#             client.get('/department')
#             self.assert_template_used('department.html')




if __name__ == '__main__':
    unittest.main()
    # flask_testing.main()
