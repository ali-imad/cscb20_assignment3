import sqlite3 

from flask import Flask, render_template, request, g
app = Flask(__name__)

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
"""
db = get.db()
db.row_factory = make_dicts

#Assuming you need student marks
students = []
for student in query_db('select _____ from students'):
    students.append(student)
db.close()

#link students to html
"""

#Getting info from database based on login
"""
-- when you try to login (when user has already submitted username/password)
sql = "SELECT * FROM _____(verification table)"

results = query_db(sql, args=(), one=False)
    for result in results:
        if result[0] ==  request.form['id'] and result[1] == request.form['password']:
            #create session
            #redirect to home page
    #if no student id found, offer them chance to sign up

"""


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/calendar')
def calendar():
    return render_template('schedule.html')


@app.route('/class-resources')
def class_resources():
    return render_template('lectures.html')



if __name__ == '__main__':
    app.run(debug=True)
