from less0n.models import *


def init_db():
    # Create tables
    print('Creating all database tables...')
    db.create_all()

    # Create data
    print('Dumping all data...')
    role_student = Role(name='student')
    db.session.add(role_student)
    role_instructor = Role(name='instructor')
    db.session.add(role_instructor)

    dept_coms = Department(id='COMS', name='Computer Science')
    db.session.add(dept_coms)

    subj_csee = Subject(id='CSEE', name='Computer Science and Electrical Engineering')
    db.session.add(subj_csee)

    db.session.commit()
    print('Done!')

if __name__ == '__main__':
    init_db()