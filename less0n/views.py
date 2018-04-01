# Reference:
# - http://bitwiser.in/2015/09/09/add-google-login-in-flask.html
# - https://stackoverflow.com/questions/34235590/how-do-you-restrict-google-login-oauth2-to-emails-from-a-specific-google-apps

from less0n import app, helpers
from less0n.models import *
import json
import logging
import re
from collections import defaultdict
from flask import url_for, redirect, render_template, session, request, flash, jsonify
from flask_login import login_required, login_user, logout_user, current_user
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


@app.route('/')
def index():
    """Return a friendly HTTP greeting."""
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
                flash('You cannot login using this email', 'error')
                return redirect(session.get('oauth_redirect', url_for('index')))

            user = User.query.filter_by(email=email).first()
            if user is None:
                user = User()
                user.email = email
            user.id = user_data['id']
            user.name = user_data['name']
            print(token)
            user.tokens = json.dumps(token)
            user.avatar = user_data['picture']
            db.session.add(user)
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


@app.route('/department', methods = ["POST", "GET"])
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
    if c is None:
        return redirect(url_for('department'))
    context = {
        'course': c,
    }
    return render_template('course-detail.html', **context)


@app.route('/course/<regex("[A-Za-z]{4}[A-Za-z0-9]{4,5}"):course_arg>/json/')
def course_json(course_arg):
    c = Course.query.filter_by(id=course_arg.upper()).first()
    if c is None:
        pass

    all_teachings = Teaching.query.filter_by(course=c).all()
    all_ratings = {}
    for teaching in all_teachings:
        prof = teaching.professor
        # Read the current ratings
        properties = all_ratings.get(prof, {})
        sum_rating = properties.get('sum_ratings', 0)
        sum_workload = properties.get('sum_workload', 0)
        sum_grade = properties.get('sum_grade', 0)
        tags_count = properties.get('tags_count', {})
        # Accumulate each new ratings
        new_comments = teaching.comments
        for comment in new_comments:
            sum_rating += comment.rating
            sum_workload += comment.rating
            sum_grade += helpers.letter_grade_to_numeric(comment.grade)
            # Count the frequency of all tags
            for tag in comment.tags:
                tags_count[tag] = tags_count.get(tag, 0) + 1
            # Only show comments that have titles or contents
            if not (not comment.title.strip()) and not (not comment.content.strip()):
                existing_comments = properties.get('comments', [])
                existing_comments.append({
                    'title': comment.title,
                    'content': comment.content,
                    'term': comment.term.id,
                    'rating': comment.rating,
                    'workload': comment.workload,
                    'grade': comment.grade,
                    'timestamp': comment.timestamp,
                })
                properties['comments'] = existing_comments
        # Store the new ratings
        properties['sum_rating'] = sum_rating
        properties['sum_workload'] = sum_workload
        properties['sum_grade'] = sum_grade
        properties['tags_count'] = tags_count
        all_ratings[prof] = properties

    # Return JSON
    ret = []
    for prof, properties in all_ratings.items():
        length = len(properties.get('comments', []))
        # Sort and find the most frequent tags
        tags_count = properties.get('tags_count', {})
        tags = [tag.text for tag in sorted(tags_count, key=tags_count.get, reverse=True)][:10]

        ret.append({
            'name': prof.name,
            'avatar': prof.avatar,
            'rating': 0 if length == 0 else properties.get('sum_rating', 0) / length,
            'workload': 0 if length == 0 else properties.get('sum_workload', 0) / length,
            'grade': 0.0 if length == 0 else properties.get('sum_grade', 0.0) / length,
            'tags': tags,
            'comments': properties.get('comments', [])
        })
    return jsonify(ret)


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500
