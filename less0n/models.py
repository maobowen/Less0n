from less0n import db, login_manager
from datetime import datetime
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.String(40), primary_key=True, nullable=False)
    avatar = db.Column(db.String(200))
    email = db.Column(db.String(40), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    tokens = db.Column(db.Text)

    def __repr__(self):
        return '<User %r>' % self.email


@login_manager.user_loader
def get_user(user_id):
    return User.query.get(user_id)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), unique=True, nullable=False)

    def __init__(self, name=None):
        db.Model.__init__(self, name=name)

    def __repr__(self):
        return '<Role %r>' % self.name


class Membership(db.Model):
    __tablename__ = 'memberships'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(40), db.ForeignKey('users.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<Membership %r>' % self.id


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.String(6), primary_key=True, nullable=False)  # COMS
    name = db.Column(db.String(40), nullable=False)  # Computer Science
    url = db.Column(db.String(200))  # Department website
    courses = db.relationship('Course', backref='course_department', lazy=True)

    def __init__(self, id=None, name=None, url=None):
        db.Model.__init__(self, id=id, name=name, url=url)

    def __repr__(self):
        return '<Department %r>' % self.name


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.String(6), primary_key=True, nullable=False)  # CSEE
    name = db.Column(db.String(40), nullable=False)  # Computer Science and Electrical Engineering
    courses = db.relationship('Course', backref='course_subject', lazy=True)

    def __init__(self, id=None, name=None):
        db.Model.__init__(self, id=id, name=name)

    def __repr__(self):
        return '<Subject %r>' % self.name


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.String(12), primary_key=True, nullable=False)  # CSEE3827
    subject = db.Column(db.String(6), db.ForeignKey('subjects.id'), nullable=False)  # CSEE
    number = db.Column(db.String(6), nullable=False)  # 3827
    name = db.Column(db.String(40), nullable=False)  # Fundamentals of Computer Systems
    department = db.Column(db.String(6), db.ForeignKey('departments.id'), nullable=False)  # COMS

    def __init__(self, id=None, subject=None, number=None, name=None, department=None):
        db.Model.__init__(self, id=id, subject=subject, number=number, name=name, departmen=department)

    def __repr__(self):
        return '<Course %r>' % self.id


class Professor(db.Model):
    __tablename__ = 'professors'
    uni = db.Column(db.String(8), primary_key=True, nullable=False)  # etl2115
    name = db.Column(db.String(100), nullable=False)  # Ewan Lowe
    department_id = db.Column(db.String(6), db.ForeignKey('departments.id'), nullable=False)  # COMS
    avatar = db.Column(db.String(200))  # Avatar
    url = db.Column(db.String(200))  # Personal website

    def __repr__(self):
        return '<Professor %r>' % self.name


class Teaching(db.Model):
    __tablename__ = 'teachings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 1
    course = db.Column(db.String(12), db.ForeignKey('courses.id'))  # CSEE3827
    professor = db.Column(db.String(8), db.ForeignKey('professors.uni'))  # Ewan Lowe
    comments = db.relationship('Comment', backref='teaching_comment', lazy=True)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 1
    teaching = db.Column(db.Integer, db.ForeignKey('teachings.id'))
    title = db.Column(db.String(100))  # Great course
    content = db.Column(db.Text)  # A very good teacher
    term = db.Column(db.String(12), db.ForeignKey('terms.id'))
    rating = db.Column(db.Integer, nullable=False)  # 5
    workload = db.Column(db.Integer, nullable=False)  # 1
    grade = db.Column(db.String(2), nullable=False)  # A+
    user = db.Column(db.String(40), db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.Column(db.String(40), db.ForeignKey('tags.id'))


class Term(db.Model):
    __tablename__ = 'terms'
    id = db.Column(db.String(12), primary_key=True, nullable=False)


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 1
    text = db.Column(db.String(40), nullable=False)