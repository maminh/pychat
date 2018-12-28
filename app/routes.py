from json import loads

from flask import render_template, redirect, url_for, flash, request, Response
from flask.views import MethodView
from flask_login import login_user, current_user, logout_user, login_required
from flask_sse import sse
from peewee import DoesNotExist

from flask import session
from app import App
from app.forms import LoginForm, RegistrationForm, AddContactForm
from app.models import User, Contact
from flask_socketio import SocketIO, send

from start import socketio


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
    return Response('ok', status=200)


@App.route('/candidate', methods=['POST'])
@login_required
def send_candidate():
    data = loads(request.data)
    sse.publish(
        {'candidate': data.get('candidate'), 'username': current_user.username},
        type='candidate', channel=data.get('username')
    )
    return Response('ok', status=200)


@App.route('/')
@login_required
def index():
    return render_template(
        "index.html", contacts=Contact.select().where(Contact.from_person == current_user.id), user=current_user
    )


'''class ChatroomView(MethodView):
    def get(self):
        print(session['room'])
        return render_template('chatroom.html', title=session['room'],user=current_user)
    def post(self):
         print request.json
         session['name'] = request.json['name']
         session['room'] = request.json['room']
         print('url : {0}'.format(url_for('create_chatroom')))
         return redirect(self.get())

App.add_url_rule('/chatroom',view_func=ChatroomView.as_view('create_chatroom'))
'''


@App.route('/chatroom', methods=['POST'])
@login_required
def create_chatroom():
    print request.json
    session['name'] = request.json['name']
    session['room'] = request.json['room']
    print('url : {0}'.format(url_for('create_chatroom')))
    return Response('ok', status=200)


@App.route('/room', methods=['GET'])
@login_required
def get_room():
    if request.method == 'GET':
        print(session['room'])
        return render_template(
            "chatroom.html", title=session['room'], user=current_user, messages=[]
        )


@socketio.on("joined", namespace='/chatroom')
def joined(message):
    print('joined')
    print(message)

@socketio.on('connect', namespace='/chatroom')
def connect(message):
    print("connect")
