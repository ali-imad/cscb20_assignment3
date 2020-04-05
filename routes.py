from flask import Blueprint, render_template

routes = Blueprint('routes', __name__)

@routes.route('/')
def root():
    return render_template('index.html')

@routes.route('/schedule')
def schedule():
    return render_template('schedule.html')

@routes.route('/lectures')
def lectures():
    return render_template('lectures.html')