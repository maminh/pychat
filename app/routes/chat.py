from datetime import datetime
from json import loads, dumps

from flask import request, jsonify
from flask_login import current_user, login_required
from flask_socketio import emit, join_room

from app import socket_io, App
from app.models import Message, User
from utils.room import generate_room_name, serialize_msg


@socket_io.on('event', namespace='/chat')
def test_msg(message):
    emit('response', message, namespace='/chat')


@socket_io.on('join', namespace='/chat')
@login_required
def on_join(data):
    data = loads(data)
    room_name = generate_room_name(current_user.username, data.get('username'))
    join_room(room_name)


@socket_io.on('send_message', namespace='/chat')
@login_required
def send_msg(data):
    json = loads(data)
    room_name = generate_room_name(json.get('sender'), json.get('receiver'))
    date = json.get('date')
    time = json.get('time')[0:8]
    datetime_obj = datetime.strptime('%s %s' % (time, date), '%H:%M:%S %a %b %d %Y')
    Message.create(
        sender=User.select().where(User.username == json.get('sender')).first().id,
        receiver=User.select().where(User.username == json.get('receiver')).first().id,
        msg=json.get('msg'), datetime=datetime_obj
    )
    json['datetime'] = str(datetime_obj)
    emit('message', dumps(json), room=room_name)


@App.route('/msgs/', methods=['POST'])
@login_required
def get_msgs():
    json = loads(request.data)
    user = User.select().where(User.username == json.get('username')).first().id
    msgs = Message.select().where(
        (Message.sender == current_user.id and Message.receiver == user) |
        (Message.receiver == current_user.id and Message.sender == user)
    ).order_by(Message.datetime)
    msgs_list = map(serialize_msg, msgs)
    return jsonify(list(msgs_list))
