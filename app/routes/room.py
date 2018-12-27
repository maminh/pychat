from json import loads

from flask import request, Response
from flask_login import login_required
from flask_sse import sse

from app import App


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
    sse.publish({'username': data.get('username')}, type='join', channel=data.get('room'))
    return Response('ok', status=200)
