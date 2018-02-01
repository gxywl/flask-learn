from datetime import datetime

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_script import Manager

app = Flask(__name__)

manager =Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

@app.route('/')
def hello_world():
    #return '<h1>Hello World!</h1>'
    return render_template('index.html', current_time=datetime.utcnow())

@app.route('/user/<name>')
def user(name):
    #return '<h1>Hello, %s!</h1>' % name
    return render_template('user.html', name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500

if __name__ == '__main__':
    #app.run(debug=True)
    #要在Edit Config中加参数
    manager.run()
