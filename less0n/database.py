from less0n.models import *


def init_db():
    # Create tables
    print('Creating all database tables...')
    db.create_all()

    # Create data
    print('Dumping all data...')

    # User Data
    users = {
        'zj2226': User(id='zj2226', avatar='', email='zj2226@columbia.edu', name='Zhijian Jiang', tokens=''),
    }
    for _, user in users.items():
        db.session.add(user)
    db.session.commit()


    # Roles
    role_student = Role(name='student')
    db.session.add(role_student)
    role_instructor = Role(name='instructor')
    db.session.add(role_instructor)
    db.session.commit()

    depts = {
        'AHAR': Department(id='AHAR', name='Art History and Archaeology'),
        'COMS': Department(id='COMS', name='Computer Science'),
        'EALC': Department(id='EALC', name='East Asian Languages and Cultures'),
        'ECON': Department(id='ECON', name='Economics'),
        'HSTB': Department(id='HSTB', name='History @Barnard'),
        'HUMC': Department(id='HUMC', name='Humanities (College)'),
        'MATH': Department(id='MATH', name='Mathematics'),
        'MUSI': Department(id='MUSI', name='Music'),
        'STAT': Department(id='STAT', name='Statistics'),
    }
    for _, dept in depts.items():
        db.session.add(dept)
    db.session.commit()

    subjs = {
        'ASCE': Subject(id='ASCE', name='Asian Civilization: East Asian'),
        'COMS': Subject(id='COMS', name='Computer Science'),
        'CSEE': Subject(id='CSEE', name='Computer Science and Electrical Engineering'),
        'ECON': Subject(id='ECON', name='Economics'),
        'HIST': Subject(id='HIST', name='History'),
        'HUMA': Subject(id='HUMA', name='Humanities'),
        'MATH': Subject(id='MATH', name='Mathematics'),
        'STAT': Subject(id='STAT', name='Statistics'),
    }
    for _, subj in subjs.items():
        db.session.add(subj)
    db.session.commit()

    courses = {
        'ASCE1359': Course(id='ASCE1359', subject=subjs['ASCE'].id, number='1359', department=depts['EALC'].id,
                           name='Introduction to East Asian Civilizations: China'),
        'ASCE1361': Course(id='ASCE1361', subject=subjs['ASCE'].id, number='1361', department=depts['EALC'].id,
                           name='Introduction to East Asian Civilizations: Japan'),
        'ASCE1363': Course(id='ASCE1363', subject=subjs['ASCE'].id, number='1363', department=depts['EALC'].id,
                           name='Introduction to East Asian Civilizations: Korea'),

        'COMS3157': Course(id='COMS3157', subject=subjs['COMS'].id, number='3157', department=depts['COMS'].id,
                           name='Advanced Programming'),
        'COMS3261': Course(id='COMS3261', subject=subjs['COMS'].id, number='3261', department=depts['COMS'].id,
                           name='Computer Science Theory'),
        'COMS4115': Course(id='COMS4115', subject=subjs['COMS'].id, number='4115', department=depts['COMS'].id,
                           name='Programming Languages and Translators'),
        'COMS4156': Course(id='COMS4156', subject=subjs['COMS'].id, number='4156', department=depts['COMS'].id,
                           name='Advanced Software Engineering'),
        'COMS4701': Course(id='COMS4701', subject=subjs['COMS'].id, number='4701', department=depts['COMS'].id,
                           name='Artificial Intelligence'),
        'COMS4705': Course(id='COMS4705', subject=subjs['COMS'].id, number='4705', department=depts['COMS'].id,
                           name='Natural Language Processing'),
        'COMS4771': Course(id='COMS4771', subject=subjs['COMS'].id, number='4771', department=depts['COMS'].id,
                           name='Machine Learning'),
        'CSEE3827': Course(id='CSEE3827', subject=subjs['CSEE'].id, number='3827', department=depts['COMS'].id,
                           name='Fundamentals of Computer Systems'),

        'ECON1105': Course(id='ECON1105', subject=subjs['ECON'].id, number='1105', department=depts['ECON'].id,
                           name='Principles of Economics'),

        'HIST1302': Course(id='HIST1302', subject=subjs['HIST'].id, number='1302', department=depts['HSTB'].id,
                           name='European History Since 1789'),

        'HUMA1001': Course(id='HUMA1001', subject=subjs['HUMA'].id, number='1001', department=depts['HUMC'].id,
                           name='Masterpieces of Western Literature and Philosophy I'),
        'HUMA1002': Course(id='HUMA1002', subject=subjs['HUMA'].id, number='1002', department=depts['HUMC'].id,
                           name='Masterpieces of Western Literature and Philosophy II'),
        'HUMA1121': Course(id='HUMA1121', subject=subjs['HUMA'].id, number='1121', department=depts['AHAR'].id,
                           name='Masterpieces of Western Art'),
        'HUMA1123': Course(id='HUMA1123', subject=subjs['HUMA'].id, number='1123', department=depts['MUSI'].id,
                           name='Masterpieces of Western Music'),

        'MATH1101': Course(id='MATH1101', subject=subjs['MATH'].id, number='1101', department=depts['MATH'].id,
                           name='Calculus I'),
        'MATH1102': Course(id='MATH1102', subject=subjs['MATH'].id, number='1102', department=depts['MATH'].id,
                           name='Calculus II'),
        'MATH1201': Course(id='MATH1201', subject=subjs['MATH'].id, number='1201', department=depts['MATH'].id,
                           name='Calculus III'),
        'MATH1202': Course(id='MATH1202', subject=subjs['MATH'].id, number='1202', department=depts['MATH'].id,
                           name='Calculus IV'),
        'MATH2010': Course(id='MATH2010', subject=subjs['MATH'].id, number='2010', department=depts['MATH'].id,
                           name='Linear Algebra'),

        'STAT4001': Course(id='STAT4001', subject=subjs['STAT'].id, number='4001', department=depts['STAT'].id,
                           name='Introduction to Probability and Statistics'),
    }
    for _, course in courses.items():
        db.session.add(course)
    db.session.commit()

    profs = {
        'mak2191': Professor(uni='mak2191', name='Martha A. Kim', department=depts['COMS'].id,
                             url='http://www.cs.columbia.edu/~martha/'),
        'cs2035': Professor(uni='cs2035', name='Clifford Stein', department=depts['COMS'].id,
                             url='http://www.columbia.edu/~cs2035/'),
    }
    for _, prof in profs.items():
        db.session.add(prof)
    db.session.commit()

    # tag data
    tags = {
        1: Tag(id=1, text="Interesting"),
        2: Tag(id=2, text="Hot"),
        3: Tag(id=3, text="Ace Professor"),
    }
    for _, tag in tags.items():
        db.session.add(tag)
    db.session.commit()

    # Term Data
    terms = {
        "Spring": Term(id="Spring"),
        "Summer": Term(id="Summer"),
        "Fall": Term(id="Fall"),
        "Winter": Term(id="Winter"),
    }
    for _, term in terms.items():
        db.session.add(term)
    db.session.commit()

    # Teaching Data
    teachings = {
        1: Teaching(id=1, course='COMS4701', professor='mak2191'),
        2: Teaching(id=2, course='COMS4705', professor='cs2035')
    }
    for _, teaching in teachings.items():
        db.session.add(teaching)
    db.session.commit()

    from datetime import datetime
    # Comment Data
    comments = {
        1: Comment(id=1, teaching=1, title='Great Course', content='A very good teacher', term='Spring',
                   rating=5, workload=1, grade='A+', user='zj2226', timestamp=datetime.now(), tags=1),
    }
    for _, comment in comments.items():
        db.session.add(comment)
    db.session.commit()





    print('Done!')


def drop_db():
    db.session.remove()
    db.drop_all()


if __name__ == '__main__':
    drop_db()
    init_db()
