from less0n.models import *

if __name__ == '__main__':
    # Create tables
    print('Creating all database tables...')
    db.create_all()

    # Create data
    print('Dumping all data...')
    role_student = Role()
    role_student.name = 'student'
    db.session.add(role_student)
    role_teacher = Role()
    role_teacher.name = 'teacher'
    db.session.add(role_teacher)

    db.session.commit()
    print('Done!')
