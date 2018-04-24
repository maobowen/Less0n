import sys
import os.path
import unittest
from unittest import mock
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from less0n import app, database
from less0n.models import *
from config import Auth


class MainTest(unittest.TestCase):
    """This class uses the Flask tests app to run an integration test against a
    local instance of the server."""

    def setUp(self):
        self.app = app.test_client()
        database.drop_db() # drop previous db
        database.init_db()

    def tearDown(self):
        database.drop_db()
        database.init_db()

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
        for test_case in '/course/COMS3157/json/', '/course/COMS4156/json/':
            rv = self.app.get(test_case)
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

    @mock.patch('flask_login.utils._get_user')
    def testAddProfToRequestDbWithValidArg(self, current_user):
        """
        Test if add_new_prof() return
        Test case:
        --------------------------------------------------
        Input                                              Expected Output
        {
        'name': 'Clifford Stein',
        'department': 'COMS',
        'semester': 'Fall',
        'year': '2016'
        }
        """
        test_cases = (
            {'name': 'Clifford Stein', 'department': 'COMS', 'course': 'COMS4701', 'semester': 'Fall', 'year': '2016'},
        )

        current_user.return_value = User.query.filter_by(id='zj2226').first()  # Mocking current_user
        for test_case in test_cases:
            rv = self.app.post('/prof/new/', data=dict(
                name=test_case['name'],
                department=test_case['department'],
                course=test_case['course'],
                semester=test_case['semester'],
                year=test_case['year'],
            ))
            assert rv._status_code == 302
            assert rv.content_type == 'text/html; charset=utf-8'
            profs = AddProfRequest.query.filter_by(name=test_case['name'],
                                                   department_id=test_case['department'], course_id=test_case['course'],
                                                   term_id=test_case['semester'] + ' ' + test_case['year']).all()
            assert profs is not None
            assert len(profs) > 0

            # delete records
            for prof in profs:
                db.session.delete(prof)
            db.session.commit()

    @mock.patch('flask_login.utils._get_user')
    def testAddProfToRequestDbWithInvalidArg(self, current_user):
        """
        Test if add_new_prof() return
        Test case:
        --------------------------------------------------
        Input                                              Expected Output
        {
        'name': 'Clifford Stein',
        'department_id': 'COMS'
        }
        """
        test_cases = (
            {'name': 'Clifford Stein', 'department': 'COMS'},
            {'name': 'Alpha Beta', 'department': 'AAAA', 'course': 'No Course', 'semester': 'Fall 2017', 'year': 2017}
        )

        current_user.return_value = User.query.filter_by(id='zj2226').first()  # Mocking current_user
        for test_case in test_cases:
            rv = self.app.post('/prof/new/', data=dict(
                name=test_case['name'],
                department=test_case['department'],
            ))
            assert rv.status == '404 NOT FOUND'

    def testApproveNewProfWithValidArg(self):
        """
        Test if admin_approve_prof_request() return
        Test case:
        --------------------------------------------------
        Input                                              Expected Output
        {                                                   200 OK
        'id': 1
        'uni': 'ab1234',
        'name': 'Alpha Beta',
        'department_id': 'COMS',
        'term_id': 'Fall 2017',
        'avatar': '',
        'url': '',
        'approved': 'Approved'
        }
        """
        test_cases = (
            {
                'id': 1,
                'uni': 'ab1234',
                'name': 'Alpha Beta',
                'department': 'COMS',
                'semester': 'Fall 2017',
                'avatar': '',
                'url': '',
                'decision': True,
                'course': 'COMS4115'
            },
            {
                'id': 1,
                'uni': 'ab1234',
                'name': 'Alpha Beta',
                'department': 'COMS',
                'semester': 'Fall 2017',
                'avatar': '',
                'url': '',
                'decision': False,
                'course': 'COMS4115'
            },
            {
                'id': -1,
                'uni': 'ab1234',
                'name': 'Alpha Beta',
                'department': 'COMS',
                'semester': 'Fall 2017',
                'avatar': '',
                'url': '',
                'decision': True,
                'course': 'COMS4115'
            }
        )

        # current_user.return_value = User.query.filter_by(id='zj2226').first()  # Mocking current_user
        for test_case in test_cases:
            rv = self.app.post('/admin/prof', data=dict(
                request_id=test_case['id'],
                uni=test_case['uni'],
                name=test_case['name'],
                department=test_case['department'],
                semester=test_case['semester'],
                avatar=test_case['avatar'],
                url=test_case['url'],
                course=test_case['course'],
                decision=test_case['decision']
            ))
            assert rv._status_code == 200

            if test_case['decision']:
                prof = Professor.query.filter_by(uni=test_case['uni']).first()
                assert prof is not None

                teachings = Teaching.query.filter_by(course_id=test_case['course'],
                                                     professor_uni=test_case['uni']).all()

                assert teachings is not None
                assert len(teachings) > 0

                # check request
                if not test_case['id'] == -1:
                    add_prof_request = AddProfRequest.query.filter_by(id=test_case['id']).first()
                    assert add_prof_request is not None
                    assert add_prof_request.approved == ApprovalType.APPROVED

                # delete records
                db.session.delete(prof)

                for teaching in teachings:
                    db.session.delete(teaching)

                db.session.commit()

            elif not test_case['decision']:
                # check request
                add_prof_request = AddProfRequest.query.filter_by(id=test_case['id']).first()
                assert add_prof_request is not None
                assert add_prof_request.approved == ApprovalType.DECLINED

    def testApproveNewProfWithUnvalidArg(self):
        """
        Test if admin_approve_prof_request() return
        Test case:
        --------------------------------------------------
        Input                                              Expected Output
        """
        test_cases = (
            {
                'id': 1,
                'user_id': 'zj2226',
                'uni': 'ab1234',
                'name': 'Alpha Beta',
                'department_id': 'AAAA',
                'term_id': 'Fall 2017',
                'avatar': '',
                'url': '',
                'approved': True,
                'course_id': 'COMS4115'
            },
            {
                'id': 1,
                'user_id': 'zj2226',
                'uni': 'ab1234',
                'name': 'Alpha Beta',
                'department_id': 'COMS',
                'term_id': '',
                'avatar': '',
                'url': '',
                'approved': True,
                'course_id': 'COMS4115'
            }
        )

        # current_user.return_value = User.query.filter_by(id='zj2226').first()  # Mocking current_user
        for test_case in test_cases:
            rv = self.app.post('/admin/prof', data=dict(
                request_id=test_case['id'],
                uni=test_case['uni'],
                name=test_case['name'],
                department=test_case['department_id'],
                semester=test_case['term_id'],
                avatar=test_case['avatar'],
                url=test_case['url'],
                course=test_case['course_id'],
                decision=test_case['approved']
            ))
            assert rv._status_code == 404
            # assert rv.content_type == 'text/html; charset=utf-8'

    def testApproveNewCourseWithValidArg(self):
        """
        Test if admin_approve_prof_request() return
        Test case:
        --------------------------------------------------
        Input                                              Expected Output
        {                                                   200 OK
        'id': 1,
        'subject': 'COMS',
        'course_num': '3137',
        'course_name': 'Honors Data Structures and Algorithms',
        'department': 'COMS',
        'semester': 'Fall 2017',
        'decision': True
        }
        """
        test_cases = (
            {
                'id': 1,
                'subject': 'COMS',
                'course_num': '3137',
                'course_name': 'Honors Data Structures and Algorithms',
                'department': 'COMS',
                'semester': 'Fall 2017',
                'decision': True
            },
        )

        # current_user.return_value = User.query.filter_by(id='zj2226').first()  # Mocking current_user
        for test_case in test_cases:
            rv = self.app.post('/admin/course', data=dict(
                request_id=test_case['id'],
                subject=test_case['subject'],
                course_num=test_case['course_num'],
                course_name=test_case['course_name'],
                department=test_case['department'],
                semester=test_case['semester'],
                decision=test_case['decision']
            ))
            assert rv._status_code == 200

            if test_case['decision']:
                course = Course.query.filter_by(id=(test_case['subject'] + test_case['course_num'])).first()
                assert course is not None

                # check request
                if not test_case['id'] == -1:
                    add_course_request = AddCourseRequest.query.filter_by(id=test_case['id']).first()
                    assert add_course_request is not None
                    assert add_course_request.approved == ApprovalType.APPROVED

                # delete records
                db.session.delete(course)

                db.session.commit()

            elif not test_case['decision']:
                # check request
                add_prof_request = AddProfRequest.query.filter_by(id=test_case['id']).first()
                assert add_prof_request is not None
                assert add_prof_request.approved == ApprovalType.DECLINED

    def testApproveNewCourseWithUnvalidArg(self):
        """
        Test if admin_approve_prof_request() return
        Test case:
        --------------------------------------------------
        Input                                              Expected Output
        {                                                   404
        'id': 1,
        'subject': 'COMS',
        'course_num': '3137',
        'course_name': 'Honors Data Structures and Algorithms',
        'department': '',
        'semester': 'Fall 2017',
        'decision': True
        }
        """
        test_cases = (
            {
                'id': 1,
                'subject': 'COMS',
                'course_num': '3137',
                'course_name': 'Honors Data Structures and Algorithms',
                'department': '',
                'semester': 'Fall 2017',
                'decision': True
            },
        )

        # current_user.return_value = User.query.filter_by(id='zj2226').first()  # Mocking current_user
        for test_case in test_cases:
            rv = self.app.post('/admin/course', data=dict(
                request_id=test_case['id'],
                subject=test_case['subject'],
                course_num=test_case['course_num'],
                course_name=test_case['course_name'],
                department=test_case['department'],
                semester=test_case['semester'],
                decision=test_case['decision']
            ))
            assert rv._status_code == 404

    def testProfWithValidArg(self):
        """
        test /prof/<regex("[A-Za-z]{2,3}[0-9]{1,4}"):prof_arg>/
        :return:
        """
        test_cases = ('/prof/etl2115/', '/prof/rt2515/')
        for test_case in test_cases:
            rv = self.app.get(test_case)
            assert rv.status_code == 200
            if test_case == '/prof/etl2115/':
                assert 'Ewan' in rv.data.decode('utf-8')

    def testProfWithInvalidArg(self):
        """
        test /prof/<regex("[A-Za-z]{2,3}[0-9]{1,4}"):prof_arg>/
        :return:
        """
        test_cases = ('/prof/ss1111/', )
        for test_case in test_cases:
            rv = self.app.get(test_case)
            assert rv.status_code == 404

    # @mock.patch('flask_login.utils._get_user')
    # def testCommentWithValidArg(self, current_user):
    #     """
    #
    #     :return:
    #     """
    #     test_cases = (
    #         {'prof': 'etl2115', 'course': 'COMS4156', 'semester': 'Spring', 'year': '2018', 'title': 'Title', 'content': 'Content',
    #          'rating': 5, 'workload': 5, 'grade': 'A+', 'tags_str': 'tag1,tag2'},
    #     )
    #     for test_case in test_cases:
    #         current_user.return_value = User.query.filter_by(id='zj2226').first()  # Mocking current_user
    #         rv = self.app.post('/comment/', data=dict(
    #             prof=test_case['prof'],
    #             course=test_case['course'],
    #             semester=test_case['semester'],
    #             year=test_case['year'],
    #             title=test_case['title'],
    #             content=test_case['content'],
    #             rating=test_case['rating'],
    #             workload=test_case['workload'],
    #             grade=test_case['grade'],
    #             tags=test_case['tags_str']
    #         ))
    #         # assert rv.status_code == 200
    #         # clean records
    #         teaching = Teaching.query.filter_by(course_id=test_case['course'].upper(),
    #                                             professor_uni=test_case['prof'].lower()).first()
    #         assert teaching is not None
    #         term = Term.query.filter_by(id=test_case['semester'] + ' ' + test_case['year'])
    #
    #         assert term is not None
    #
    #
    #         comment = Comment.query.filter_by(user_id=current_user.return_value.id,
    #                                            teaching=teaching,
    #                                            term=term).first()
    #         assert comment is not None



if __name__ == '__main__':
    unittest.main()
