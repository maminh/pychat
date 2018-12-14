from json import loads

from flask import render_template, redirect, url_for, flash, request, Response
from flask_login import login_user, current_user, logout_user, login_required
from flask_sse import sse
from peewee import DoesNotExist

from app import App
from app.forms import LoginForm, RegistrationForm, AddContactForm
from app.models import User, Contact


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


@App.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@App.route('/add_contact', methods=['GET', 'POST'])
@login_required
def add_contact():
    form = AddContactForm()
    if form.validate_on_submit():
        Contact.get_or_create(from_person=current_user.id, to_person=form.user_id)
        return redirect(url_for('index'))
    return render_template('add_contact.html', title='add contact', form=form)


@App.route('/offer', methods=['POST'])
@login_required
def send_offer():
    data = loads(request.data)
    sse.publish(
        {'username': current_user.username, 'offer': data.get('offer')}, type='offer', channel=data.get('username')
    )
    return Response('ok', status=200)


@App.route('/answer', methods=['POST'])
@login_required
def send_answer():
    data = loads(request.data)
    sse.publish(
        {'answer': data.get('answer'), 'username': current_user.username}, type='answer', channel=data.get('username')
    )
    return Response('', status=201)


@App.route('/candidate', methods=['POST'])
@login_required
def send_candidate():
    data = loads(request.data)
    print(data)
    sse.publish(
        {'candidate': data.get('candidate'), 'username': current_user.username},
        type='candidate', channel=data.get('username')
    )
    return Response('', status=201)


@App.route('/')
@login_required
def index():
    return render_template(
        "index.html", contacts=Contact.select().where(Contact.from_person == current_user.id), user=current_user
    )


@App.route('/hello')
def publish_hello():
    sse.publish({"message": "Hello!"}, type='greeting', channel=current_user.username)
    return "Message sent!"
