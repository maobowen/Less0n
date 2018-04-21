# Reference:
# - http://bitwiser.in/2015/09/09/add-google-login-in-flask.html
# - https://stackoverflow.com/questions/34235590/how-do-you-restrict-google-login-oauth2-to-emails-from-a-specific-google-apps

from less0n import app, helpers, db
from less0n.models import *
import json
import logging
import re
from collections import defaultdict
from flask import url_for, redirect, render_template, session, request, flash, jsonify, abort
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.expression import ClauseElement
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError
from werkzeug.routing import BaseConverter
from config import Auth


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter


def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(Auth.CLIENT_ID, state=state, redirect_uri=app.config['GOOGLE_OAUTH_REDIRECT_URI'])
    oauth = OAuth2Session(Auth.CLIENT_ID, redirect_uri=app.config['GOOGLE_OAUTH_REDIRECT_URI'], scope=Auth.SCOPE)
    return oauth


def has_membership(user_id, role):
    membership = Membership.query.filter_by(user_id=user_id, role=role).first()
    return membership is not None


def get_or_create(model, defaults=None, **kwargs):
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.items() if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        db.session.add(instance)
        return instance, True


@app.context_processor
def injection():
    return {'now': datetime.utcnow()}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    session['oauth_redirect'] = request.args.get('redirect') or url_for('index')
    if current_user.is_authenticated:
        return redirect(session['oauth_redirect'])

    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline', prompt='select_account')
    session['oauth_state'] = state
    return redirect(auth_url)


@app.route('/oauth')
def oauth2callback():
    # Redirect user to home page if already logged in.
    if current_user is not None and current_user.is_authenticated:
        return redirect(session.get('oauth_redirect', url_for('index')))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:
        # Execution reaches here when user has
        # successfully authenticated our app.
        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(
                Auth.TOKEN_URI,
                client_secret=Auth.CLIENT_SECRET,
                authorization_response=request.url)
        except HTTPError:
            return 'HTTPError occurred.'
        google = get_google_auth(token=token)
        resp = google.get(Auth.USER_INFO)
        if resp.status_code == 200:
            user_data = resp.json()
            email = user_data['email']
            uni, hd = email.split('@')
            if (hd != 'columbia.edu' and hd != 'barnard.edu') or not re.compile(r'([a-z]{2,3}\d{1,4})').match(uni):
                flash('You cannot login using this email. Please use Lionmail instead.', 'danger')
                return redirect(session.get('oauth_redirect', url_for('index')))

            # Register user
            user = User.query.filter_by(email=email).first()
            if user is None:
                user = User()
                user.email = email
            user.id = uni
            user.name = user_data['name']
            print(token)
            user.tokens = json.dumps(token)
            user.avatar = user_data['picture']
            db.session.add(user)
            db.session.commit()

            # Register membership
            role_student = Role.query.filter_by(name='student').first()
            role_instructor = Role.query.filter_by(name='instructor').first()
            if not has_membership(user.id, role_instructor) and not has_membership(user.id, role_student):
                db.session.add(Membership(user=user, role=role_student))
                db.session.commit()

            login_user(user)
            return redirect(session.get('oauth_redirect', url_for('index')))
        return 'Could not fetch your information.'


@app.route('/logout')
@login_required
def logout():
    redirect_url = request.args.get('redirect') or url_for('index')
    logout_user()
    session.clear()
    return redirect(redirect_url)


@app.route('/department', methods=["GET", "POST"])
def department():
    """
    Render the template with all departments if it is the "GET" request.
    Render the template with departments having keywords if it is the "POST" request.
    :return: rendered template
    """
    if request.method == "GET":
        all_depts = Department.query.all()
        context = {'depts': all_depts}
        return render_template('department.html', **context)

    elif request.method == "POST":
        dept_keyword = request.form['dept_keyword']
        depts = Department.query.filter(Department.name.contains(dept_keyword)).all()
        context = {'depts': depts}
        return render_template('department.html', **context)


@app.route('/dept/<regex("[A-Za-z]{4}"):dept_arg>/')
def department_course(dept_arg):
    dept = Department.query.filter_by(id=dept_arg.upper()).first()
    if dept is None:
        return redirect(url_for('department'))

    statistics = {}
    all_courses = Course.query.filter_by(department=dept).all()
    for c in all_courses:
        sum_rating = sum_workload = sum_grade = 0
        count_all_comments = count_nonempty_comments = 0
        statistics[c] = {}

        all_teachings = Teaching.query.filter_by(course=c).all()
        if len(all_teachings) == 0:  # If there is no teaching, return -1 for rating, workload and grade
            statistics[c]['rating'] = statistics[c]['workload'] = statistics[c]['grade'] = -1
            statistics[c]['comment'] = 0
        else:  # Otherwise, iterate each teaching
            for teaching in all_teachings:
                all_comments = teaching.comments
                for comment in all_comments:  # Iterate each comment
                    count_all_comments += 1
                    sum_rating += comment.rating
                    sum_workload += comment.workload
                    sum_grade += helpers.letter_grade_to_numeric(comment.grade)
                    if not (not comment.title.strip()) and not (not comment.content.strip()):
                        count_nonempty_comments += 1

            if count_all_comments == 0:  # If there is no comment, return -1 for rating, workload and grade
                statistics[c]['rating'] = statistics[c]['workload'] = statistics[c]['grade'] = -1
                statistics[c]['comment'] = 0
            else:
                statistics[c]['rating'] = sum_rating / count_all_comments
                statistics[c]['workload'] = sum_workload / count_all_comments
                statistics[c]['grade'] = sum_grade / count_all_comments
                statistics[c]['comment'] = count_nonempty_comments

    context = {
        'dept': dept,
        'courses': statistics,
    }
    return render_template('department-course.html', **context)


@app.route('/course/<regex("[A-Za-z]{4}[A-Za-z0-9]{4,5}"):course_arg>/')
def course(course_arg):
    c = Course.query.filter_by(id=course_arg.upper()).first()
    depts = Department.query.all()
    if c is None:
        return redirect(url_for('department'))
    context = {
        'course': c,
        'depts': depts,
    }
    return render_template('course-detail.html', **context)


@app.route('/course/<regex("[A-Za-z]{4}[A-Za-z0-9]{4,5}"):course_arg>/json/')
def course_json(course_arg):
    c = Course.query.filter_by(id=course_arg.upper()).first()
    if c is None:
        abort(404)

    all_teachings = Teaching.query.filter_by(course=c).all()
    all_statistics = {}

    # Statistics of all professors
    all_profs_sum_rating = all_profs_sum_workload = all_profs_sum_grade = 0
    all_profs_tags_count = {}
    all_profs_count_all_comments = 0
    all_profs_nonempty_comments = []

    for teaching in all_teachings:
        # Statistics of the current professor in the current teaching
        # Each professor in all_teachings is unique
        cur_prof = teaching.professor
        cur_prof_sum_rating = cur_prof_sum_workload = cur_prof_sum_grade = 0
        cur_prof_tags_count = {}
        cur_prof_count_all_comments = 0
        cur_prof_nonempty_comments = []

        # Accumulate each ratings
        all_comments = teaching.comments
        for comment in all_comments:
            cur_prof_sum_rating += comment.rating
            cur_prof_sum_workload += comment.workload
            cur_prof_sum_grade += helpers.letter_grade_to_numeric(comment.grade)
            cur_prof_count_all_comments += 1
            all_profs_sum_rating += comment.rating
            all_profs_sum_workload += comment.workload
            all_profs_sum_grade += helpers.letter_grade_to_numeric(comment.grade)
            all_profs_count_all_comments += 1

            # Count the frequency of all tags
            for tag in comment.tags:
                cur_prof_tags_count[tag] = cur_prof_tags_count.get(tag, 0) + 1
                all_profs_tags_count[tag] = all_profs_tags_count.get(tag, 0) + 1

            # Only show comments that have titles or contents
            if not (not comment.title.strip()) and not (not comment.content.strip()):
                json_comment = {
                    'title': comment.title,
                    'content': comment.content,
                    'term': comment.term.id,
                    'rating': comment.rating,
                    'workload': comment.workload,
                    'grade': comment.grade,
                    'timestamp': comment.timestamp,
                }
                cur_prof_nonempty_comments.append(json_comment)
                all_profs_nonempty_comments.append(json_comment)

        # Store ratings of the current professor
        all_statistics[cur_prof] = {
            'sum_rating': cur_prof_sum_rating,
            'sum_workload': cur_prof_sum_workload,
            'sum_grade': cur_prof_sum_grade,
            'tags_count': cur_prof_tags_count,
            'count_all_comments': cur_prof_count_all_comments,
            'nonempty_comments': cur_prof_nonempty_comments,
        }

    # Return JSON
    ret = []
    # Return statistics of all professors
    all_profs_tags = [tag.text for tag in sorted(all_profs_tags_count, key=all_profs_tags_count.get, reverse=True)][:10]
    ret.append({
        'name': 'All Instructors',
        'uni': None,
        'avatar': '',
        'rating': -1 if all_profs_count_all_comments == 0 else all_profs_sum_rating / all_profs_count_all_comments,
        'workload': -1 if all_profs_count_all_comments == 0 else all_profs_sum_workload / all_profs_count_all_comments,
        'grade': -1 if all_profs_count_all_comments == 0 else all_profs_sum_grade / all_profs_count_all_comments,
        'tags': all_profs_tags,
        'comments': all_profs_nonempty_comments,
    })
    # Return statistics of each professor
    for cur_prof, cur_prof_statistics in all_statistics.items():
        # Sort and find the most frequent tags
        cur_prof_tags_count = cur_prof_statistics['tags_count']
        cur_prof_tags = [tag.text for tag in sorted(cur_prof_tags_count, key=cur_prof_tags_count.get, reverse=True)][:10]
        cur_prof_count_all_comments = cur_prof_statistics['count_all_comments']

        ret.append({
            'name': cur_prof.name,
            'uni': cur_prof.uni,
            'avatar': cur_prof.avatar,
            'rating': -1 if cur_prof_count_all_comments == 0 else cur_prof_statistics['sum_rating'] / cur_prof_count_all_comments,
            'workload': -1 if cur_prof_count_all_comments == 0 else cur_prof_statistics['sum_workload'] / cur_prof_count_all_comments,
            'grade': -1 if cur_prof_count_all_comments == 0 else cur_prof_statistics['sum_grade'] / cur_prof_count_all_comments,
            'tags': cur_prof_tags,
            'comments': cur_prof_statistics['nonempty_comments'],
        })
    return jsonify(ret)


@app.route('/course/new/', methods=['GET', 'POST'])
@login_required
def add_new_course():
    """
    Add course request

    Request form example:
    {
        'course_name': 'Computer Networks',
        'course_number': 'CSEE4119',
        'department_name': 'Computer Science',
        'subject_name': 'Computer Science and Electrical Engineering'
    }

    :return: json-str.
        "OK" if add successfully. "Fail" + error info if subject / department / professor not exists.
    """
    redirect_url = request.args.get('redirect') or url_for('index')
    if request.method == "GET":
        depts = Department.query.all()
        subjs = Subject.query.all()
        context = {
            'depts': depts,
            'subjs': subjs,
            'redirect_url': redirect_url,
        }
        return render_template('add-course.html', **context)

    elif request.method == "POST":
        # Pre check
        form_arguments = {'course-name', 'course-number', 'department', 'subject', 'semester', 'year'}
        for arg in form_arguments:
            if arg not in request.form:
                abort(404)

        # Retrieve request arguments
        course_name = request.form.get('course-name', type=str)
        course_number = request.form.get('course-number', type=str)
        department_id = request.form.get('department', type=str)
        subject_id = request.form.get('subject', type=str)
        course_id = subject_id + course_number
        term_id = request.form.get('semester', type=str) + ' ' + request.form.get('year', type=str)

        # Post check
        department = Department.query.filter_by(id=department_id).first()
        subject = Subject.query.filter_by(id=subject_id).first()
        for param in (course_id, course_name, course_number, department, subject, term_id):  # None or empty
            if not param:
                flash('The values you have input are invalid. Please check and submit again.', 'danger')
                return redirect(redirect_url)

        # Add request to database
        try:
            term, _ = get_or_create(Term, id=term_id)
            add_course_request = AddCourseRequest(
                course_id=course_id, course_name=course_name, course_number=course_number,
                department=department, subject=subject, term=term,
                user_id=current_user.id, approved=ApprovalType.PENDING)
            db.session.add(add_course_request)
            db.session.commit()
            flash('The adding course request is submitted.', 'success')
        except SQLAlchemyError:
            flash('An error occurred when submitting an adding course request.', 'danger')
        return redirect(redirect_url)


@app.route('/search/', methods=['GET'])
def search():
    """
    Search department, subject, professor and course
    :param
        request example
            {'dept': 'COMS', 'subj': 'COMS', 'prof': 'daniel', course: 'COMS4156', }
    :return: rendered template

    Examples:
        /search/?prof=daniel
    """
    context = {}
    context['count'] = 0

    # get keywords
    dept = request.args.get('dept')
    subj = request.args.get('subj')
    prof = request.args.get('prof')
    course = request.args.get('course')

    if dept is not None:
        depts = re.split(',\s*|\s+', dept)  # split keywords by , |\s
        results = []
        for dept in depts:
            for result in Department.query.filter((Department.id.like("%%" + dept + "%")) |
                                                  (Department.name.like("%%" + dept + "%"))).all():
                results.append(result)
        context['depts'] = results
        context['count'] += len(results)

    if subj is not None:
        subjs = re.split(',\s*|\s+', subj)
        results = []
        for subj in subjs:
            for result in Subject.query.filter((Subject.id.like("%%" + subj + "%")) |
                                               (Subject.name.like("%%" + subj + "%"))).all():
                results.append(result)
        context['subjs'] = results
        context['count'] += len(results)

    if prof is not None:
        profs = re.split(',\s*|\s+', prof)
        results = []
        for prof in profs:
            for result in Professor.query.filter((Professor.uni.like("%%" + prof + "%")) |
                                                 (Professor.name.like("%%" + prof + "%"))).all():
                results.append(result)
        context['profs'] = results
        context['count'] += len(results)

    if course is not None:
        courses = re.split(',\s*|\s+', course)
        results = []
        for course in courses:
            for result in Course.query.filter((Course.id.like("%%" + course + "%")) |
                                              (Course.name.like("%%" + course + "%"))).all():
                results.append(result)
        context['courses'] = results
        context['count'] += len(results)
    return render_template('search-result.html', **context)


@app.route('/prof/<regex("[A-Za-z]{2,3}[0-9]{1,4}"):prof_arg>/')
def prof(prof_arg):
    prof = Professor.query.filter_by(uni=prof_arg.lower()).first()
    if prof is None:
        abort(404)

    all_teachings = Teaching.query.filter_by(professor=prof).all()
    statistics = {}  # Statistics of each course
    # Statistics of all courses
    all_courses_sum_rating = all_courses_sum_workload = all_courses_sum_grade = all_courses_count_all_comments = 0
    all_courses_tags_count = {}
    all_statistics = {}

    # Statistics of all courses (i.e. all teachings)
    for teaching in all_teachings:
        c = teaching.course
        cur_course_sum_rating = cur_course_sum_workload = cur_course_sum_grade = 0
        cur_course_count_all_comments = cur_course_count_nonempty_comments = 0
        statistics[c] = {}

        all_comments = teaching.comments
        for comment in all_comments:  # Iterate each comment
            cur_course_count_all_comments += 1
            cur_course_sum_rating += comment.rating
            cur_course_sum_workload += comment.workload
            cur_course_sum_grade += helpers.letter_grade_to_numeric(comment.grade)
            if not (not comment.title.strip()) and not (not comment.content.strip()):
                cur_course_count_nonempty_comments += 1

            all_courses_count_all_comments += 1
            all_courses_sum_rating += comment.rating
            all_courses_sum_workload += comment.workload
            all_courses_sum_grade += helpers.letter_grade_to_numeric(comment.grade)
            # Count the frequency of all tags
            for tag in comment.tags:
                all_courses_tags_count[tag] = all_courses_tags_count.get(tag, 0) + 1

        # Calculate ratings for the current course
        if cur_course_count_all_comments == 0:  # If there is no comment, return N/A for rating, workload and grade
            statistics[c]['rating'] = statistics[c]['workload'] = statistics[c]['grade'] = -1
            statistics[c]['comment'] = 0
        else:
            statistics[c]['rating'] = cur_course_sum_rating / cur_course_count_all_comments
            statistics[c]['workload'] = cur_course_sum_workload / cur_course_count_all_comments
            statistics[c]['grade'] = cur_course_sum_grade / cur_course_count_all_comments
            statistics[c]['comment'] = cur_course_count_nonempty_comments

    # Calculate ratings for the professor
    all_statistics['tags'] = [tag.text for tag in sorted(all_courses_tags_count, key=all_courses_tags_count.get, reverse=True)][:10]
    if all_courses_count_all_comments == 0:  # If there is no comment, return N/A for rating, workload and grade
        all_statistics['rating'] = all_statistics['workload'] = all_statistics['grade'] = -1
    else:
        all_statistics['rating'] = all_courses_sum_rating / all_courses_count_all_comments
        all_statistics['workload'] = all_courses_sum_workload / all_courses_count_all_comments
        all_statistics['grade'] = all_courses_sum_grade / all_courses_count_all_comments

    context = {
        'prof': prof,
        'courses': statistics,
        'prof_stats': all_statistics,
    }
    return render_template('faculty-page.html', **context)


@app.route('/prof/new/', methods=['POST'])
def add_new_prof():
    """
    Add professor request
    Request form example:
    {
        'name': 'Clifford Stein',
        'department_id': 'COMS',
        'term_id': 'Fall 2016'
    }
    :return: json-str.
        "OK" if add successfully. "Fail" + error info if subject / department / professor not exists.
    """
    redirect_url = request.args.get('redirect') or url_for('index')

    # Pre check
    form_arguments = {'name', 'department', 'course', 'semester', 'year'}
    for arg in form_arguments:
        if arg not in request.form:
            abort(404)

    # Retrieve request arguments
    name = request.form.get('name', type=str)
    department_id = request.form.get('department', type=str)
    course_id = request.form.get('course', type=str)
    term_id = request.form.get('semester', type=str) + ' ' + request.form.get('year', type=str)

    # Post check
    department = Department.query.filter_by(id=department_id).first()
    course = Course.query.filter_by(id=course_id).first()
    for param in (name, department, course, term_id):  # None or empty
        if not param:
            flash('The values you have input are invalid. Please check and submit again.', 'danger')
            return redirect(redirect_url)

    # Add request to database
    try:
        term, _ = get_or_create(Term, id=term_id)
        add_prof_request = AddProfRequest(
            name=name, department=department, course=course, term=term,
            user_id=current_user.id, approved=ApprovalType.PENDING)
        db.session.add(add_prof_request)
        db.session.commit()
        flash('The adding instructor request is submitted.', 'success')
        return redirect(redirect_url)
    except SQLAlchemyError:
        flash('An error occurred when submitting an adding instructor request.', 'danger')
        return redirect(redirect_url, code=500)


@app.route('/comment/', methods=["POST"])
@login_required
def comment():
    if request.method == "POST":
        redirect_url = request.args.get('redirect') or url_for('index')
        # Retrieve teaching
        prof_uni = request.form.get('prof', type=str)
        course_id = request.form.get('course', type=str)
        teaching = Teaching.query.filter_by(course_id=course_id.upper(), professor_uni=prof_uni.lower()).first()
        if teaching is None:
            abort(500)
        # Retrieve request arguments
        term_id = request.form.get('semester', type=str) + ' ' + request.form.get('year', type=str)
        title = request.form.get('title', type=str)
        content = request.form.get('message', type=str)
        rating = request.form.get('rating', type=int)
        workload = request.form.get('workload', type=int)
        grade = request.form.get('grade', type=str)
        tags_str = request.form.get('tags', type=str)
        # Post check
        if rating > 6 or rating < 1 \
                or workload > 6 or workload < 1 \
                or not re.compile('^[A-DF]$|^[A-C][\+-]$').match(grade):
            flash('The values you have input are invalid. Please check and submit again.', 'danger')
            return redirect(redirect_url)
        tags_str_list = tags_str.split(',')
        # Insert
        try:
            tags = []
            for t in tags_str_list:
                if t:  # Neither None nor empty string
                    tag, _ = get_or_create(Tag, text=t.capitalize())
                    tags.append(tag)
            term, _ = get_or_create(Term, id=term_id)

            # Check if existed
            existed_comment = Comment.query.filter_by(user_id=current_user.id, teaching=teaching, term=term).first()
            if existed_comment is not None:
                flash('You have already published an evaluation before.', 'danger')
            else:
                comment = Comment(user_id=current_user.id, teaching=teaching, term=term,
                                  title=title, content=content, rating=rating, workload=workload, grade=grade, tags=tags)
                db.session.add(comment)
                db.session.commit()
                flash('The evaluation is published.', 'success')
            return redirect(redirect_url)
        except SQLAlchemyError:
            flash('An error occurred when publishing the evaluation.', 'danger')
            return redirect(redirect_url, code=500)


@app.route('/admin/', methods=['GET'])
@login_required
def admin():
    """Return the admin page, or redirect to index page if not authorized."""
    role_admin = Role.query.filter_by(name='admin').first()
    if current_user.is_authenticated and has_membership(current_user.id, role_admin):
        return render_template('admin.html')
    else:
        flash('You do not have the permission to view this page.', 'danger')
        return redirect(url_for('index'), code=401)


@app.route('/admin/course', methods=['GET'])
@login_required
def admin_list_course_request():
    """Return a JSON containing adding course requests, or raise 401 if not authorized."""
    role_admin = Role.query.filter_by(name='admin').first()
    if current_user.is_authenticated and has_membership(current_user.id, role_admin):
        list_approved = request.args.get('approved', type=int) or 0
        list_pending = request.args.get('pending', type=int) or 0
        list_declined = request.args.get('declined', type=int) or 0
        course_requests = []
        if list_approved:
            course_requests.extend(AddCourseRequest.query.filter_by(approved=ApprovalType.APPROVED).all())
        if list_pending:
            course_requests.extend(AddCourseRequest.query.filter_by(approved=ApprovalType.PENDING).all())
        if list_declined:
            course_requests.extend(AddCourseRequest.query.filter_by(approved=ApprovalType.DECLINED).all())
        ret = []
        for course_request in course_requests:
            ret.append({
                'id': course_request.id,
                'subject_id': course_request.subject.id,
                'course_number': course_request.course_number,
                'course_name': course_request.course_name,
                'department_id': course_request.department.id,
                'term_id': course_request.term.id,
                'approved': course_request.approved.value,
            })
        return jsonify(ret)
    else:
        abort(401)


@app.route('/admin/prof', methods=['GET'])
@login_required
def admin_list_prof_request():
    """Return a JSON containing adding instructor requests, or raise 401 if not authorized."""
    role_admin = Role.query.filter_by(name='admin').first()
    if current_user.is_authenticated and has_membership(current_user.id, role_admin):
        list_approved = request.args.get('approved', type=int) or 0
        list_pending = request.args.get('pending', type=int) or 0
        list_declined = request.args.get('declined', type=int) or 0
        prof_requests = []
        if list_approved:
            prof_requests.extend(AddProfRequest.query.filter_by(approved=ApprovalType.APPROVED).all())
        if list_pending:
            prof_requests.extend(AddProfRequest.query.filter_by(approved=ApprovalType.PENDING).all())
        if list_declined:
            prof_requests.extend(AddProfRequest.query.filter_by(approved=ApprovalType.DECLINED).all())
        ret = []
        for prof_request in prof_requests:
            ret.append({
                'id': prof_request.id,
                'name': prof_request.name,
                'department_id': prof_request.department.id,
                'course_id': prof_request.course.id,
                'term_id': prof_request.term.id,
                'approved': prof_request.approved.value,
            })
        return jsonify(ret)
    else:
        abort(401)


# Routes for admins
@app.route('/admin/course', methods=['POST'])
def approve_new_course():
    """
    Admin approves a course.
    - Add a new course to Course entity
    - Add a new teaching to Teaching entity

    :return: json-str.
        "OK" if add successfully. "Fail" + error info if subject / department / professor not exists.
    """
    redirect_url = request.args.get('redirect') or url_for('index')

    # get parameters
    course_name = request.form["course-name"]
    course_number = request.form["course-number"]
    professor_name = request.form["professor-name"]
    department_name = request.form["department-name"]

    # check parameters
    for param in (course_name, course_number, professor_name, department_name):
        if param == None or len(param) == 0:
            return redirect(redirect_url, code='404')

    # extract parameters
    subject_id = course_number[0: 4] # COMS4156 -> COMS
    number = course_number[len(course_number) - 4: ]

    # get objects
    subject = Subject.query.filter(Subject.id.contains(subject_id)).first()
    department = Department.query.filter(Department.name.contains(department_name)).first()
    professor = Professor.query.filter(Professor.name.contains(professor_name)).first()

    # check objects
    for obj in (subject, department, professor):
        if obj == None:
            return redirect(redirect_url, code='404')

    # construct objects
    course = Course(id=course_number, subject=subject, number=number, department=department, name=course_name)
    teaching = Teaching(professor=professor, course=course)

    # add to db
    db.session.add(course)
    db.session.add(teaching)
    db.session.commit()
    return jsonify('OK')


@app.route('/admin/prof', methods=['POST'])
def approve_new_prof():
    """
    Admin approves a prof.

    Example:
    {
        "id": 1,
        "uni": "ab1234",
        "prof_name: "Alpha Beta",
        "department_id": "COMS",
        "term_id": "Fall 2017",
        "course_id": "COMS4115",
        "avatar": "",
        "url": "",
        "approved": "Declined"
    }

    :return: json-str.
        "OK" if add successfully. "Fail" + error info if subject / department / professor not exists.
    """
    redirect_url = request.args.get('redirect') or url_for('index')

    # get parameters
    id = request.form['id']
    uni = request.form['uni']
    prof_name = request.form["name"]
    department_id = request.form["department_id"]
    term_id = request.form["term_id"]
    avatar = request.form['avatar']
    url = request.form['url']
    course_id = request.form['course_id']
    approved = request.form['approved']

    approved_types = {'Approved': ApprovalType.APPROVED, 'Pending': ApprovalType.PENDING,
                     'Declined': ApprovalType.DECLINED}

    # check parameters
    for param in (id, uni, prof_name, department_id, term_id, course_id, approved):
        if param == None or len(param) == 0:
            return redirect(redirect_url, code='404')

    # check if this professor exists
    if approved == 'Declined':
        pass

    elif approved == 'Approved':
        # get objects
        department = Department.query.filter_by(id=department_id).first()
        term = Term.query.filter_by(id=term_id).first()
        course = Course.query.filter_by(id=course_id).first()

        # check objects
        for obj in (department, term, course):
            if obj is None:
                return redirect(redirect_url, code='404')

        # update professor if not exist
        professor = Professor(uni=uni, name=prof_name, department=department,
                         avatar=avatar, url=url)
        if Professor.query.filter_by(uni=uni).first() is not None:
            # construct objects
            db.session.add(professor)

        # update teaching if not exist
        teaching = Teaching(course=course, professor=professor)
        if len(Teaching.query.filter_by(course_id=course_id, professor_uni=uni).all()) == 0:
            db.session.add(teaching)

    # update the approved column
    new_prof_request = AddProfRequest.query.filter_by(id=id).first()
    new_prof_request.approved = approved_types[approved]
    db.session.commit()

    return jsonify('OK')


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


@app.errorhandler(404)
def page_not_found_error(e):
    logging.exception('Page not found.')
    return render_template('404.html'), 404
