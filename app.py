import sqlite3, os, secrets, logging

from flask import Flask, flash, render_template, request, g, session, request, redirect, abort, url_for
from wtforms import Form, StringField, PasswordField, TextAreaField, validators, SelectField, DecimalField
from flask.logging import create_logger
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base

#### INIT ####
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# favicon
app.add_url_rule('/favicon.ico', redirect_to=url_for('static', filename='favicon.ico'))

# database initializations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
db = SQLAlchemy(app)

# grabbing tables
Base = automap_base()
Base.prepare(db.engine, reflect=True)

# assigning tables to variables
Verification = Base.classes.verification
Remarks = Base.classes.remarks
Students = Base.classes.students
Instructors = Base.classes.instructors
Feedback = Base.classes.feedback


LOG = create_logger(app)


#### CLASSES ####
class RegisterForm(Form):
    student_id = StringField('Student ID', [validators.Length(min=6, max=20, message='Student ID must be between 6 to 20 characters')])
    student_name = StringField('Full Name', [validators.Length(min=4, max=80, message="Please enter your full name.")])
    student_pw = PasswordField('Password', [
        validators.Length(min=3, max=18, message='Password must be between 3 to 18 characters'),
        validators.EqualTo('confirm_pw', message='Passwords must match')
    ])
    confirm_pw = PasswordField('Confirm Password', [validators.Length(min=3, max=18)])


class LoginForm(Form):
    user_id = StringField('User ID', [validators.DataRequired(message="Please fill in the user ID field.")])
    user_pw = PasswordField('User Password', [validators.DataRequired(message="Please fill in the password field.")])


class UpdateGradeForm(Form):
    assignment = SelectField('Assignment', choices=[('A1', 'Assignment 1'),
                                                    ('A2', 'Assignment 2'),
                                                    ('A3', 'Assignment 3'),
                                                    ('Midterm', 'Midterm'),
                                                    ('Final', 'Final'),
                                                    ('Labs', 'Labs')
                                                    ])

    new_grade = DecimalField('New grade', [validators.DataRequired(message="Please enter a value"), validators.NumberRange(min=0, message="Please enter a value greater than 0.")], places=2)


class FeedbackForm(Form):
    q1 = TextAreaField(u"What do you like about the instructor teaching?")
    q2 = TextAreaField(u"What do you recommend the instructor to do to improve their teaching?")
    q3 = TextAreaField(u"What do you like about the instructor's assignments and testing material?")
    q4 = TextAreaField(u"Do you believe you are being properly evaluated on your knowledge in this course?")
    instructor = SelectField("Instructor of interest", choices=[])


# everything below this in the """""" i'm not using
"""
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

"""

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
        return render_template('index.html', student_info=student_info, is_student=session.get('student'))
    elif session.get('instructor') is True:
        instructor_info = session.get('intructor_info')
        all_students = session.get('all_students')
        return render_template('index.html', instructor_info=instructor_info, all_students=all_students, is_student=session.get('student'))

@app.route('/login', methods=['GET', 'HEAD'])
def not_logged_in():
    if session.get('student') or session.get('instructor'):
        return redirect('/')
    form = LoginForm(request.form)
    return render_template('login.html', form=form)


@app.route('/login', methods=['POST'])
def login():
    # connecting to database to get usernames and passwords
    form = LoginForm(request.form)
    user_id = form.user_id.data
    user_pw = form.user_pw.data

    if form.validate():
        verification_list = db.session.query(Verification).all()
        for user in verification_list:
            # verify they're in the system
            if user.username == user_id and user.password == user_pw:
                # check if they're a student or an instructor
                instructor_list = db.session.query(Instructors).all()
                for instructor in instructor_list:
                    if instructor.PID == user_id:
                        session['instructor'] = True
                        break
                else:
                    student_list = db.session.query(Students).all()
                    for student in student_list:
                        if student.SID == user_id:
                            session['student'] = True
                            break

                session['ID'] = user_id
                return redirect('/')
        
    flash("Please enter a valid id/password combination.")
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    if session.get('student'):
        LOG.info("Goodbye, student")
        session.pop('student',None)
    elif session.get('instructor'):
        LOG.info("Goodbye, instructor")
        session.pop('instructor',None)
    return redirect('/')

@app.route('/register', methods=['GET', 'HEAD'])
def not_registered(): 
    if session.get('student') or session.get('instructor'):
        return redirect('/')
    form = RegisterForm(request.form)
    LOG.info("Form established.")
    return render_template('signup.html', form=form)


@app.route('/register', methods=['POST'])
def register():
    form = RegisterForm(request.form)
    LOG.info("Form established.")
    if form.validate():
        new_user_verify = Verification(username=form.student_id.data, password=form.student_pw.data)
        new_user_grades = Students(SID=form.student_id.data,
                                    Name=form.student_name.data,
                                    A1=None,
                                    A2=None,
                                    A3=None,
                                    Midterm=None,
                                    Final=None,
                                    Labs=None
                                    )
        db.session.add(new_user_grades)
        db.session.add(new_user_verify)
        db.session.commit()
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
    # jinja specific bools
    is_student = session.get('student')
    is_instructor = session.get('instructor')
    all_students = {}
    student_info = {}
    all_remarks = {}

    if is_instructor:
        # build the dictionary only if we are logged in as an instructor
        student_list = db.session.query(Students).all()
        for student in student_list:
            all_students[student.SID] = student.__dict__

        remark_list = db.session.query(Remarks).all()
        for remark in remark_list:
            all_remarks[remark.request_id] = {
                'request_id': remark.request_id,
                'remark' : remark.remark,
                'explanation': remark.explanation,
                'request_user': remark.request_user
            }


    elif is_student:
        student = db.session.query(Students).get(session.get('ID'))
        student_info = student.__dict__

    return render_template('marks.html', student_info=student_info, is_student=is_student, all_students=all_students, all_remarks=all_remarks)


@app.route('/marks/<student_id>', methods=['GET', 'HEAD', 'POST'])
def edit_marks(student_id):
    if not session.get('instructor'):
        return redirect('/marks')
    session['canMark'] = bool(db.session.query(Instructors).get(session.get('ID')).canMark)
    if not session.get('canMark'):
        return redirect('/marks')
    
    student = db.session.query(Students).get(student_id)
    if student is None:
        flash('{0} was not a valid student ID!'.format(student_id))
        return redirect('/marks')
    student_info = student.__dict__
    form = UpdateGradeForm(request.form)
    if request.method == 'POST' and form.validate():
        setattr(student, form.assignment.data, float(form.new_grade.data))
        db.session.commit()
        flash("Marks updated!")
        return redirect('/marks')
    
    return render_template('edit_marks.html', student_info=student_info, form=form)
    


@app.route('/feedback', methods=['GET', 'HEAD', 'POST'])
def feedback():
    is_student = session.get('student')
    all_feedback = {}
    form = FeedbackForm(request.form)
    # build the instructor choices from the names of all active instructors
    # their id's are the values
    form.instructor.choices = [(instruct.PID, instruct.Name) for instruct in db.session.query(Instructors).all()]
    if not is_student:
        feedback_list = db.session.query(Feedback).all()
        for feedback in feedback_list:
            if feedback.PID == session.get('ID'):
                all_feedback[feedback.feedback_id] = feedback.__dict__

    if request.method == 'POST' and form.validate():
        new_feedback = Feedback(PID=form.instructor.data, q1=form.q1.data, q2=form.q1.data, q3=form.q1.data, q4=form.q1.data)
        db.session.add(new_feedback)
        db.session.commit()
        flash("Thanks for the feedback!")
        return redirect(url_for('root'))
    
    return render_template("feedback.html", is_student=is_student, all_feedback=all_feedback, form=form)


if __name__ == '__main__':
    app.run(debug=True)
