import os
from json import loads

from flask import render_template, redirect, url_for, flash, request, Response
from flask_login import login_user, current_user, logout_user, login_required
from flask_sse import sse
from peewee import DoesNotExist

from app import App, ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from app.forms import LoginForm, RegistrationForm, VideoForm
from app.models import User


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


@App.route('/offer', methods=['POST'])
@login_required
def send_offer():
    data = loads(request.data)
    sse.publish(
        {'offer': data.get('offer')}, type='offer', channel=data.get('room')
    )
    return Response('ok', status=200)


@App.route('/answer', methods=['POST'])
@login_required
def send_answer():
    data = loads(request.data)
    sse.publish(
        {'answer': data.get('answer')}, type='answer', channel=data.get('room')
    )
    return Response('ok', status=200)


@App.route('/candidate', methods=['POST'])
@login_required
def send_candidate():
    data = loads(request.data)
    sse.publish(
        {'candidate': data.get('candidate')},
        type='candidate', channel=data.get('room')
    )
    return Response('ok', status=200)


@App.route('/join_room', methods=['POST'])
@login_required
def join_room():
    data = loads(request.data)
    sse.publish({'username': data.get('username')}, type='join', channel=data.get('room'))
    return Response('ok', status=200)


@App.route('/')
@login_required
def index():
    return render_template("index.html", user=current_user)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def connection_exists():
    return True

@App.route('/record', methods=['GET', 'POST'])
@login_required
def upload():

    form = VideoForm()
    if request.method == 'GET':
        print(current_user)
        return  render_template('videochat.html')
    elif request.method == 'POST':
        if form.validate_on_submit():
            print(current_user)
            file = request.files['file']
            if allowed_file(file.filename):
                file.save(os.path.join(UPLOAD_FOLDER + '/streams', str(current_user)+'-'+str(form.chatID.data)+'-'
                                       + str(form.streamID.data)+'.mp4'))
                return Response('ok',status=200)
        print(form.errors)
        return Response('Bad request',400)
