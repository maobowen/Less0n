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
    user_id = db.Column(db.String(40), db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    __table_args__ = (
        db.UniqueConstraint('user_id', 'role_id', name='_memberships_uc'),
    )

    def __repr__(self):
        return '<Membership %r>' % self.id


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.String(6), primary_key=True, nullable=False)  # COMS
    name = db.Column(db.String(100), unique=True, nullable=False)  # Computer Science
    url = db.Column(db.String(200))  # Department website
    courses = db.relationship('Course', backref='department', lazy=True)

    def __init__(self, id=None, name=None, url=None):
        db.Model.__init__(self, id=id, name=name, url=url)

    def __repr__(self):
        return '<Department %r>' % self.name


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.String(6), primary_key=True, nullable=False)  # CSEE
    name = db.Column(db.String(100), unique=True, nullable=False)  # Computer Science and Electrical Engineering
    courses = db.relationship('Course', backref='subject', lazy=True)

    def __init__(self, id=None, name=None):
        db.Model.__init__(self, id=id, name=name)

    def __repr__(self):
        return '<Subject %r>' % self.name


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.String(12), primary_key=True, nullable=False)  # CSEE3827
    subject_id = db.Column(db.String(6), db.ForeignKey('subjects.id'), nullable=False)  # CSEE
    number = db.Column(db.String(6), nullable=False)  # 3827
    name = db.Column(db.String(100), nullable=False)  # Fundamentals of Computer Systems
    department_id = db.Column(db.String(6), db.ForeignKey('departments.id'), nullable=False)  # COMS

    def __init__(self, id=None, subject=None, number=None, name=None, department=None):
        db.Model.__init__(self, id=id, subject=subject, number=number, name=name, department=department)

    def __repr__(self):
        return '<Course %r>' % self.id


class Professor(db.Model):
    __tablename__ = 'professors'
    uni = db.Column(db.String(8), primary_key=True, nullable=False)  # etl2115
    name = db.Column(db.String(100), nullable=False)  # Ewan Lowe
    department_id = db.Column(db.String(6), db.ForeignKey('departments.id'), nullable=False)  # COMS
    department = db.relationship('Department', backref='professors', lazy=True)
    avatar = db.Column(db.String(200))  # Avatar
    url = db.Column(db.String(200))  # Personal website

    def __init__(self, uni=None, name=None, department=None, avatar='', url=''):
        db.Model.__init__(self, uni=uni, name=name, department=department, avatar=avatar, url=url)

    def __repr__(self):
        return '<Professor %r>' % self.name


class Teaching(db.Model):
    __tablename__ = 'teachings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 1
    course_id = db.Column(db.String(12), db.ForeignKey('courses.id'), nullable=False)  # CSEE3827
    course = db.relation(Course, backref='teachings', lazy=True)
    professor_uni = db.Column(db.String(8), db.ForeignKey('professors.uni'), nullable=False)  # Ewan Lowe
    professor = db.relation(Professor, backref='teachings', lazy=True)
    comments = db.relationship('Comment', backref='teaching', lazy=True)
    __table_args__ = (
        db.UniqueConstraint('course_id', 'professor_uni', name='_teachings_uc'),
    )


class Term(db.Model):
    __tablename__ = 'terms'
    id = db.Column(db.String(12), primary_key=True, nullable=False)


comments_tags = db.Table(
    'comments_tags',
    db.Column('comment', db.Integer, db.ForeignKey('comments.id'), primary_key=True),
    db.Column('tag', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 1
    teaching_id = db.Column(db.Integer, db.ForeignKey('teachings.id'), nullable=False)
    title = db.Column(db.String(100))  # Great course
    content = db.Column(db.Text)  # A very good teacher
    term_id = db.Column(db.String(12), db.ForeignKey('terms.id'), nullable=False)
    term = db.relation(Term, backref='comments', lazy=True)
    rating = db.Column(db.Integer, nullable=False)  # 5
    workload = db.Column(db.Integer, nullable=False)  # 1
    grade = db.Column(db.String(2), nullable=False)  # A+
    user_id = db.Column(db.String(40), db.ForeignKey('users.id'), nullable=False)
    user = db.relation(User, backref='comments', lazy=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tags = db.relationship('Tag', secondary=comments_tags, lazy='subquery', backref=db.backref('comments', lazy=True))


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 1
    text = db.Column(db.String(40), nullable=False)


class CourseRequest(db.Model):
    __tablename__ = 'course_requests'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 1
    user_id = db.Column(db.String(40))  # zj2226
    course_id = db.Column(db.String(12), nullable=False)  # CSEE3827
    name = db.Column(db.String(100), nullable=False)  # Fundamentals of Computer Systems
    department = db.Column(db.String(100), nullable=False)  # Computer Science
    subject = db.Column(db.String(100), nullable=False)  # Computer Science and Electrical Engineering
    approved = db.Column(db.String(7))  # False, True, Pending

    def __repr__(self):
        return '<Course %r>' % self.course_id
