from json import loads, dumps

from flask import request, Response
from flask_login import login_required
from flask_sse import sse

from app import App, mem_cache
from utils.room import serialize_cache


@App.route('/room/offer', methods=['POST'])
@login_required
def send_offer():
    data = loads(request.data)
    sse.publish(
        {'offer': data.get('offer')}, type='offer', channel=data.get('room')
    )
    return Response('ok', status=200)


@App.route('/room/answer', methods=['POST'])
@login_required
def send_answer():
    data = loads(request.data)
    sse.publish(
        {'answer': data.get('answer')}, type='answer', channel=data.get('room')
    )
    return Response('ok', status=200)


@App.route('/room/candidate', methods=['POST'])
@login_required
def send_candidate():
    data = loads(request.data)
    sse.publish(
        {'candidate': data.get('candidate')},
        type='candidate', channel=data.get('room')
    )
    return Response('ok', status=200)


@App.route('/room/join_room', methods=['POST'])
@login_required
def join_room():
    data = loads(request.data)
    room = serialize_cache(data.get('room'))
    if not room:
        return Response('room not found', status=404)
    room['members'] += [data.get('username')]
    mem_cache.set(data.get('room'), room)
    sse.publish({'username': data.get('username')}, type='join', channel=data.get('room'))
    return Response(dumps(room), status=200)


@App.route('/room/create_room', methods=['POST'])
@login_required
def create_room():
    data = loads(request.data)
    room = mem_cache.get(data.get('room'))
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
def send_signal():
    data = loads(request.data)
    sse.publish({'data': data.get('data')}, type=data.get('type'), channel=data.get('room'))
    return Response('ok', status=200)
