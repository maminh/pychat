import os

from flask import render_template, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user
from peewee import DoesNotExist

from app import App, profiles
from app.forms import LoginForm, RegistrationForm
from app.models import User


@App.route('/user/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        filename = user.username + os.path.splitext(form.photo.data.filename)[1]
        user.set_password(form.password.data)
        # TODO: remove hostname from profile url
        user.profile = profiles.url(filename)
        profiles.save(form.photo.data, name=filename)
        user.save()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@App.route('/user/login/', methods=['GET', 'POST'])
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


@App.route('/user/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))
