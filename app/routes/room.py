from json import loads, dumps

from flask import request, Response, render_template
from flask_login import login_required, current_user
from flask_sse import sse

from app import App, mem_cache
from utils.room import serialize_cache


@App.route('/room/video')
@login_required
def video_room():
    return render_template('video_room.html', user=current_user)


@App.route('/room/voice')
@login_required
def voice_room():
    return render_template('voice_room.html', user=current_user)


@App.route('/room/offer', methods=['POST'])
@login_required
def send_offer():
    data = loads(request.data)
    room = serialize_cache(data.get('room'))
    if room.get('creator') != current_user.username:
        return Response('unauthorized', status=403)
    for member in room.get('members', []):
        sse.publish(
            {'offer': data.get('offer')}, type='offer', channel='user_{}'.format(member)
        )
    return Response('ok', status=200)


@App.route('/room/answer', methods=['POST'])
@login_required
def send_answer():
    data = loads(request.data)
    room = serialize_cache(data.get('room'))
    for member in room.get('members', []):
        if member == current_user.username:
            continue
        sse.publish(
            {'answer': data.get('answer')}, type='answer', channel='user_{}'.format(member)
        )
    sse.publish(
        {'answer': data.get('answer')}, type='answer', channel='user_{}'.format(room.get('creator'))
    )
    return Response('ok', status=200)


@App.route('/room/candidate', methods=['POST'])
@login_required
def send_candidate():
    data = loads(request.data)
    room = serialize_cache(data.get('room'))
    for member in room.get('members', []):
        if member == current_user.username:
            continue
        print(current_user.username, member)
        sse.publish({'candidate': data.get('candidate')}, type='candidate', channel='user_{}'.format(member))
    print(room.get('creator'))
    if room.get('creator') != current_user.username:
        sse.publish({'candidate': data.get('candidate')}, type='candidate',
                    channel='user_{}'.format(room.get('creator')))
        print('user_{}'.format(room.get('creator')))
    return Response('ok', status=200)


@App.route('/room/join_room', methods=['POST'])
@login_required
def join_room():
    data = loads(request.data)
    room = serialize_cache(data.get('room'))
    if not room:
        return Response('room not found', status=404)
    room['members'] += [data.get('username')]
    mem_cache.set(data.get('room'), room, expire=2 * 60)
    sse.publish({'username': data.get('username')}, type='join', channel=data.get('room'))
    return Response(dumps(room), status=200)


@App.route('/room/create_room', methods=['POST'])
@login_required
def create_room():
    data = loads(request.data)
    room = mem_cache.get(data.get('room'))
    if data.get('room')[0:5] == "user_":
        return Response('room name cannot started with _user!', status=400)
    if room:
        return Response('already exists', status=409)
    room_data = {
        'creator': data.get('username'),
        'members': []
    }
    mem_cache.set(data.get('room'), room_data, expire=2 * 60)
    sse.publish({'username': data.get('username')}, type='join', channel=data.get('room'))
    return Response('ok', status=200)


@App.route('/room/send_signal/', methods=['POST'])
@login_required
def send_room_signal():
    data = loads(request.data)
    sse.publish({'data': data.get('data')}, type=data.get('type'), channel=data.get('room'))
    return Response('ok', status=200)
