import sqlite3, os, secrets, logging 

from flask import Flask, flash, render_template, request, g, session, request, redirect, abort, url_for
from wtforms import Form, StringField, PasswordField, validators
from flask.logging import create_logger
#from flask_sqlalchemy import SQLAlchemy

#### CLASSES ####
class RegisterForm(Form):
    student_id = StringField('Username', [validators.Length(min=6, max=20, message='Student ID must be between 6 to 20 characters')])
    student_name = StringField('Full Name', [validators.Length(min=4, max=80, message="Please enter your full name.")])
    student_pw = PasswordField('Password', [
        validators.Length(min=3, max=16, message='Password must be between 3 to 16 characters'),
        validators.EqualTo('confirm_pw', message='Passwords must match')
    ])
    confirm_pw = PasswordField('Confirm Password', [validators.Length(min=3, max=16)])


#db = SQLAlchemy()
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
LOG = create_logger(app)


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
    if not (session.get('student') or session.get('instructor')):
        return redirect('/login')
    elif session.get('student') is True:
        student_info = session.get('student_info')
        return render_template('index.html', student_info = student_info, is_student=session.get('student'))
    elif session.get('instructor') is True:
        instructor_info = session.get('intructor_info')
        all_students = session.get('all_students')
        return render_template('index.html', instructor_info=instructor_info, all_students=all_students, is_student=session.get('student'))

@app.route('/login', methods=['GET', 'HEAD'])
def not_logged_in():
    return render_template('login.html')


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
        LOG.info("Goodbye, student")
        session.pop('student',None)
    elif session.get('instructor'):
        LOG.info("Goodbye, instructor")
        session.pop('instructor',None)
    return redirect('/')

@app.route('/register', methods=['GET', 'HEAD', 'POST'])
def not_registered(): 
    if session.get('student') or session.get('instructor'):
        return redirect('/')
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO verification VALUES (?, ?)", (form.student_id.data, form.student_pw.data))
        cur.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (form.student_id.data, form.student_name.data, None, ))
        cur.close()
        db.close()
        flash('Thanks for registering!')
        return redirect('/')

    return render_template('signup.html', form=form)


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
    """
    if request.form['explanation'] != None:
        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO remarks VALUES (?, ?)", (request.form['remark'], request.form['explanation']))
        cur.close()
        db.close()
    """    
    return render_template('marks.html', student_info=student_info, is_student=is_student, all_students=all_students)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    app.run(debug=True)
