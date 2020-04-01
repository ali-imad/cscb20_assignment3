import sqlite3, os, secrets, logging 

from flask import Flask, flash, render_template, request, g, session, request, redirect, abort, url_for
#from flask_sqlalchemy import SQLAlchemy

#db = SQLAlchemy()
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'


# everything below this in the """""" i'm not using
DATABASE = './login.db'

# from flask documentatio at 
# https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/?highlight=sqlite
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# from flask documentatio at
# https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/?highlight=sqlite
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

# from flask documentatio at
# https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/?highlight=sqlite
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


# from flask documentatio at
# https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/?highlight=sqlite



##### authentication #####
# partly inspired by tutorial at
# https://pythonspot.com/login-authentication-with-flask/ 
# and https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login 

@app.route('/')
def root():
    # cookie check
    app.logger.error(session.get('student'), session.get('instructor'))
    if not (session.get('student') or session.get('instructor')):
        return render_template('login.html')
    elif session.get('student') is True:
        student_info = session.get('student_info')
        return render_template('index.html', student_info = student_info, is_student=session.get('student'))
    elif session.get('instructor') is True:
        instructor_info = session.get('intructor_info')
        all_students = session.get('all_students')
        return render_template('index.html', instructor_info=instructor_info, all_students=all_students, is_student=session.get('student'))

@app.route('/login', methods=['POST'])
def login():

    #connecting to database to get usernames and passwords
    db = get_db()

    db.row_factory = make_dicts
    verify_student= []
    verify_instructor = []
    all_students = []
    
    for student in query_db('SELECT * FROM students'):
        all_students.append(student)

    for student in query_db('SELECT * FROM verification v, students s WHERE s.sid = username'):
        verify_student.append(student)
    for instructor in query_db('SELECT * FROM verification v, instructors i WHERE v.username = i.pid'):
        verify_instructor.append(instructor)
    db.close()

    # handle authentication
    for student in verify_student:
        if request.form['pw-login'] == student['password'] and request.form['user-login'] == student['username']:
            session['student'] = True
            session['student_info'] = student
            return redirect(url_for('.root', student_info= student))
    for instructor in verify_instructor:
        if request.form['pw-login'] == instructor['password'] and request.form['user-login'] == instructor['username']:
            session['instructor'] = True
            session['instructor_info'] = instructor
            session['all_students'] = all_students
            return redirect(url_for('.root', instructor_info=instructor, all_students=all_students))
    return render_template('login.html')

@app.route('/logout')
def logout():
    # this is non functional, redirect breaks it
    if session.get('student'):
        app.logger.warning("YEP YUR A STUDENT")
        session.pop('student',None)
    elif session.get('instructor'):
        app.logger.warning("YEP YUR A instructor")
        session.pop('instructor',None)
    redirect('/')

@app.route('/calendar')
def calendar():
    return render_template('schedule.html')

@app.route('/class-resources')
def class_resources():
    return render_template('lectures.html')

@app.route('/marks')
def marks():
    student_info = session.get('student_info')
    is_student = session.get('student')
    all_students = session.get('all_students')
    return render_template('marks.html', student_info=student_info, is_student=is_student, all_students=all_students)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()




if __name__ == '__main__':
    app.run(debug=True)
