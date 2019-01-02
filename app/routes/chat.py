from json import loads

from flask_login import current_user, login_required
from flask_socketio import emit, join_room

from app import socket_io
from utils.room import generate_room_name


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
    room_name = generate_room_name(current_user.username, json.get('username'))
    emit('message', data, room=room_name)
