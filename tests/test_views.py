import sys
import os.path
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from less0n import app, database
from less0n.models import *
from config import Auth
import re


class MainTest(unittest.TestCase):
    """This class uses the Flask tests app to run an integration test against a
    local instance of the server."""

    def setUp(self):
        self.app = app.test_client()
        database.drop_db() # drop previous db
        database.init_db()

    def tearDown(self):
        database.drop_db()

    def testIndex(self):
        rv = self.app.get('/')
        data = rv.data.decode("utf-8")
        assert("Welcome to Less0n" in data)

    def testLogin(self):
        rv = self.app.get('/login')
        assert(rv._status_code == 302)
        assert(Auth.AUTH_URI in rv.location)

    # Test /department/

    def testDepartment(self):
        """
        Test if department() with GET return rendered department.html
        """
        rv = self.app.get('/department')
        assert rv._status_code == 200
        assert rv.content_type == 'text/html; charset=utf-8'
        assert 'department' in rv.data.decode('utf-8').lower()  # "department.html" must have Department

    def testDepartmentSearchWithValidInput(self):
        """
        Test if department() with POST return department.html with correct department name

        Test cases:
        --------------------------------------------------
        dept_keyword Input                Expected Output
        computer                          computer in html
        """
        rv = self.app.post('/department', data=dict(
            dept_keyword="computer"
        ))
        assert rv._status_code == 200
        assert rv.content_type == 'text/html; charset=utf-8'
        data = rv.data.decode('utf-8').lower()  # convert data to lower case
        assert 'department' in data
        # assert 'computer' in data

    def testDepartmentSearchWithInvalidInput(self):
        """
        Test if department() with POST return department.html with correct department name

        Test cases:
        --------------------------------------------------
        dept_keyword Input                Expected Output
        zhongwenxi                        No word between <section id="sort-alphabetical" data-filter-group="dept"> and </section>
        """
        rv = self.app.post('/department', data=dict(
            dept_keyword="zhongwenxi"
        ))
        assert rv._status_code == 200
        assert rv.content_type == 'text/html; charset=utf-8'
        data = rv.data.decode('utf-8').lower()  # convert data to lower case
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

    # Test /dept/DEPT/

    def test_departmentCourseWithValidArg(self):
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
        data = rv.data.decode('utf-8').lower()  # convert data to lower case
        assert 'department-course' in data
        assert 'coms' in data

    def testDepartmentCourseWithInvalidArg(self):
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
        data = rv.data.decode('utf-8').lower()  # convert data to lower case
        assert 'department' in data

    # Test /course/COURSE/

    def testCourseWithValidArg(self):
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

    def testCourseWithInvalidArg(self):
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

    # Test /course/COURSE/json

    def testCourseJsonWithValidArg(self):
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

    def testCourseJsonWithInvalidArg(self):
        """
        Test if course() return course-detail.html with valid argument
        Test case:
        --------------------------------------------------
        Input                             Expected Output
        /course/COMS1234/json             404
        /course/ABCDEFG/json              404
        """
        rv = self.app.get('/course/COMS1234/json/')
        assert rv._status_code == 404

        rv = self.app.get('/course/ABCDEFG/json/')
        assert rv._status_code == 404

    def testSearchWithValidArg(self):
        """
        Test if search() return search-result.html with valid arguments
        Test case:
        --------------------------------------------------
        Input                             Expected Output
        /search/?dept=COMS,ECON&subj=COMS,
        CSEE&prof=daniel&course=COMS      coms, econ, electrical, daniel, asce in search-result.html
        """
        rv = self.app.get('/search/?dept=COMS,ECON&subj=COMS+CSEE&prof=daniel&course=ASCE')
        assert rv._status_code == 200
        assert rv.content_type == 'text/html; charset=utf-8'
        data = rv.data.decode('utf-8').lower()  # convert data to lower case
        assert 'coms' in data
        assert 'econ' in data
        assert 'electrical engineering' in data
        # assert 'daniel' in data
        assert 'asce' in data

    def testSearchWithInvalidArg(self):
        """
        Test if search() return search-result.html with valid arguments
        Test case:
        --------------------------------------------------
        Input                             Expected Output
        /search/?dept=zhongwen            empty in the dept/course/prof/subject part of search-result.html
        """
        rv = self.app.get('/search/?dept=zhongwen')
        assert rv._status_code == 200
        assert rv.content_type == 'text/html; charset=utf-8'
        data = rv.data.decode('utf-8').lower()  # convert data to lower case

        # verify if the content part is empty
        assert re.search(r'<div class="row" id="department-card">(\n\s+)+</div>', data) != None
        assert re.search(r'<div class="row" id="subject-card">(\n\s+)+</div>', data) != None
        assert re.search(r'<div class="row" id="professor-card">(\n\s+)+</div>', data) != None
        assert re.search(r'<div class="row" id="course-card">(\n\s+)+</div>', data) != None

    def testSearchWithEmptyArg(self):
        """
        Test if search() return search-result.html with valid arguments
        Test case:
        --------------------------------------------------
        Input                             Expected Output
        /search/                          empty in the dept/course/prof/subject part of search-result.html
        """
        rv = self.app.get('/search/?dept=zhongwen')
        assert rv._status_code == 200
        assert rv.content_type == 'text/html; charset=utf-8'
        data = rv.data.decode('utf-8').lower()  # convert data to lower case

        # verify if the content part is empty
        assert re.search(r'<div class="row" id="department-card">(\n\s+)+</div>', data) != None
        assert re.search(r'<div class="row" id="subject-card">(\n\s+)+</div>', data) != None
        assert re.search(r'<div class="row" id="professor-card">(\n\s+)+</div>', data) != None
        assert re.search(r'<div class="row" id="course-card">(\n\s+)+</div>', data) != None

    '''
    def testAddProfToRequestDbWithValidArg(self):
        """
        Test if add_course_to_request_db() return
        Test case:
        --------------------------------------------------
        Input                                              Expected Output
        {
        'name': 'Clifford Stein',
        'department_id': 'COMS',
        'term_id': 'Fall 2016'
        }
        """
        test_cases = (
            {
                'name': 'Clifford Stein',
                'department_id': 'COMS',
                'term_id': 'Fall 2016'
            },
        )

        for test_case in test_cases:
            rv = self.app.post('/user/prof/request', data=dict(
                name=test_case['name'],
                department_id=test_case['department_id'],
                term_id=test_case['term_id']
            ))
            assert rv.status == '200 OK'
            assert 'ok' in rv.data.decode('utf-8').lower()
            profs = AddProfRequest.query.filter_by(name=test_case['name'],
                                                     department_id=test_case['department_id'],
                                                     term_id=test_case['term_id']).all()
            assert profs is not None
            assert len(profs) > 0

            # delete records
            for prof in profs:
                db.session.delete(prof)
            db.session.commit()

    def testAddProfToRequestDbWithInvalidArg(self):
        """
        Test if add_course_to_request_db() return
        Test case:
        --------------------------------------------------
        Input                                              Expected Output
        {
        'name': 'Clifford Stein',
        'department_id': 'COMS'
        }
        """
        test_cases = (
            {
                'name': 'Clifford Stein',
                'department_id': 'COMS'
            },
        )

        for test_case in test_cases:
            rv = self.app.post('/user/prof/request', data=dict(
                name=test_case['name'],
                department_id=test_case['department_id']
            ))
            assert rv.status == '404 NOT FOUND'
    '''

if __name__ == '__main__':
    unittest.main()
