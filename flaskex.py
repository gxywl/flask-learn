#!/usr/bin/python
#_*_ coding:utf8 _*_

from datetime import datetime

import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
from flask_migrate import Migrate, MigrateCommand
from flask_moment import Moment
from flask_script import Manager, Shell
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form, FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required, DataRequired

# --------------------

app = Flask(__name__)

# --------------------

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SECRET_KEY'] = 'hard to guess string'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

app.config['FLASKEX_AMIL_SUBJECT_PREFIX'] = '[Flaskex]'
app.config['FLASKEX_AMIL_SENDER'] = 'Flaskex Admin <gxcnywl@qq.com>'

app.config['FLASKEX_ADMIN'] = os.environ.get('FLASKEX_ADMIN')

def send_email(to, subject,template, **kwargs):
    msg = Message(app.config['FLASKEX_AMIL_SUBJECT_PREFIX'] + subject,sender = app.config['FLASKEX_AMIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)

# --------------------

db = SQLAlchemy(app)

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

migrate = Migrate(app,db)
manager.add_command('db', MigrateCommand)

mail = Mail(app)
# --------------------

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

manager.add_command("shell",Shell(make_context=make_shell_context))
# --------------------

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


# --------------------


@app.route('/', methods=['GET', 'POST'])
def index():
    # return '<h1>Hello World!</h1>'
    # return render_template('index.html', current_time=datetime.utcnow())

    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False

            if app.config['FLASKEX_ADMIN']:
                send_email(app.config['FLASKEX_ADMIN'], 'New User', 'mail/new_user', user=user)

        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known',False), current_time=datetime.utcnow())


@app.route('/user/<name>')
def user(name):
    # return '<h1>Hello, %s!</h1>' % name
    return render_template('user.html', name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# --------------------

if __name__ == '__main__':
    # app.run(debug=True)
    # 要在Edit Config中加参数
    manager.run()
