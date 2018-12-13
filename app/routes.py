from flask import render_template, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user
from flask_sse import sse
from peewee import DoesNotExist

from app import App
from app.forms import LoginForm, RegistrationForm
from app.models import User


@App.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.get(User.username == form.username.data)
        except DoesNotExist:
            flash('the username does not exists')
            return redirect(url_for('login'))

        if not user.check_password(form.password.data):
            flash('password is incorrect')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@App.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        user.save()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@App.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@App.route('/')
def index():
    return render_template("index.html")


@App.route('/hello')
def publish_hello():
    sse.publish({"message": "Hello!"}, type='greeting')
    return "Message sent!"
