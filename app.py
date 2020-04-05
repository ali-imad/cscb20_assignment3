import sqlite3, os, secrets, logging 

from flask import Flask, flash, render_template, request, g, session, request, redirect, abort, url_for
from flask.logging import create_logger
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
LOG = create_logger(app)


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
    @app.teardown_appcontext
    def close_connection(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

    #When you want to use the database use this:
    db = get.db()
    db.row_factory = make_dicts

    #Assuming you need student marks
    students = []
    for student in query_db('select _____ from students'):
        students.append(student)
    db.close()

    #link students to html
"""

##### authentication #####
# partly inspired by tutorial at
# https://pythonspot.com/login-authentication-with-flask/ 
# and https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login 

@app.route('/')
def root():
    # cookie check
    if not (session.get('student') or session.get('instructor')):
        return render_template('login.html')
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    # handle authentication
    if request.form['pw-login'] == 'pw1' and request.form['user-login'] == 'testuser':
        session['student'] = True
        return redirect('/')
    elif request.form['pw-login'] == 'instruct' and request.form['user-login'] == 'teach':
        session['instructor'] = True
        return redirect('/')
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

@app.route('/register')
def signup():
    return render_template('signup.html')

@app.route('/calendar')
def calendar():
    return render_template('schedule.html')

@app.route('/class-resources')
def class_resources():
    return render_template('lectures.html')

if __name__ == '__main__':
    app.run(debug=True)
