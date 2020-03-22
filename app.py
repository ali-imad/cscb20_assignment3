from flask import Flask, render_template
app = Flask(__name__)

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
