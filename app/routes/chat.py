import os
from datetime import datetime
from json import loads, dumps

from flask import request, jsonify, render_template, send_file, Response
from flask_login import current_user, login_required
from flask_socketio import emit, join_room
from peewee import DoesNotExist

from app import socket_io, App, ALLOWED_VIDEOS, UPLOAD_FOLDER, ALLOWED_AUDIO
from app.celery_tasks import merge_streams, merge_audio_streams
from app.forms import StreamForm
from app.models import Message, User, ChatVideos, StreamModel
from app.utils import random_name
from utils.room import generate_room_name, serialize_msg, serialize_cache


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


def allowed_video(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEOS


def allowd_audio(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO


def connection_exists():
    return True


@App.route('/record/video', methods=['GET', 'POST'])
@login_required
def upload_video():
    form = StreamForm()
    if request.method == 'GET':
        videos = ChatVideos.select().where(
            (ChatVideos.peer1 == current_user.id) | (ChatVideos.peer2 == current_user.id))
        return render_template('recorded_chats.html', videos=videos)
    elif request.method == 'POST':
        if form.validate_on_submit():
            file = request.files['file']
            print(file.filename)
            if allowed_video(file.filename):
                print('allowd file name')
                name = random_name() + '.mp4'
                file.save(os.path.join(UPLOAD_FOLDER + '/streams', name))
                print(form.chatID.data)
                try:
                    peer = User.get(User.id == current_user.id)
                except DoesNotExist:
                    return Response('Bad request', 404)
                print('priting peer user')
                print(peer)
                streamModel = StreamModel()
                streamModel.peer1ID = current_user.id
                room = serialize_cache(form.chatID.data)
                print('room', room)
                if room.get('creator') == current_user.username:
                    peer2 = User.get(User.username == room.get('members')[0])
                    print('I\'m host', str(peer2))
                    streamModel.peer2ID = peer2.id
                elif room.get('members') and room.get('members')[0] == current_user.username:
                    peer2 = User.get(User.username == room.get('creator'))
                    print('I\'m guest', str(peer2))
                    streamModel.peer2ID = peer2.id
                streamModel.streamID = form.streamID.data
                streamModel.streamName = name
                print(streamModel)
                if form.fin.data:
                    streamModel.fin = True
                try:
                    streamModel.save()
                    print('stream model saved')
                except Exception as e:
                    print(e)
                    print('stream model could not be saved')
                    return Response('Stream not saved', 400)
                print(form.fin.data)
                if form.fin.data:
                    print('merging streams')
                    if StreamModel.get_or_none(peer2ID=form.streamID.data, streamID=current_user.id, fin=True):
                        merge_streams.delay(peer1ID=current_user.id, peer2ID=form.chatID.data)
                return Response('ok', status=200)
        print(form.errors)
        return Response('Bad request', 400)


@App.route('/record/audio', methods=['GET', 'POST'])
@login_required
def upload_audio():
    form = StreamForm()
    if request.method == 'GET':
        videos = ChatVideos.select().where(
            (ChatVideos.peer1 == current_user.id) | (ChatVideos.peer2 == current_user.id))
        return render_template('recorded_chats.html', videos=videos)
    elif request.method == 'POST':
        if form.validate_on_submit():
            file = request.files['file']
            if allowd_audio(file.filename):
                name = random_name() + '.mp3'
                file.save(os.path.join(UPLOAD_FOLDER + '/streams', name))
                print(form.chatID.data)
                peer = User.get(User.username == form.chatID.data)
                print(peer)
                streamModel = StreamModel()
                streamModel.peer1ID = current_user.id
                streamModel.peer2ID = peer.id
                streamModel.streamID = form.streamID.data
                streamModel.streamName = name
                if form.fin.data:
                    streamModel.fin = True
                try:
                    streamModel.save()
                    print('stream model saved')
                except Exception as e:
                    print(e)
                    print('stream model could not be saved')
                    return Response('Stream not saved', 400)
                print(form.fin.data)
                if form.fin.data:
                    print('merging streams')
                    if StreamModel.get_or_none(peer2ID=form.streamID.data, streamID=current_user.id, fin=True):
                        merge_audio_streams.delay(peer1ID=current_user.id, peer2ID=form.chatID.data)
                return Response('ok', status=200)


@App.route('/download/<filename>')
@login_required
def get_chat_video(filename):
    print('file name is : {0}'.format(filename))
    return send_file(UPLOAD_FOLDER + '/chats', attachment_filename=filename, as_attachment=True)
