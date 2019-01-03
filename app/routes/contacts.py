from json import loads

from flask import render_template, request, Response
from flask_login import login_required, current_user

from app import App
from app.models import Contact, User


@App.route('/contacts/')
@login_required
def contacts():
    return render_template(
        'contacts.html', user=current_user,
        contacts=Contact.select().where(Contact.owner == current_user.id).order_by(Contact.contact)
    )


@App.route('/contacts/add/', methods=['POST'])
@login_required
def add_contact():
    try:
        data = loads(request.data)
    except TypeError:
        return Response('data is not valid'), 400

    user = User.select().where(User.username == data.get('username')).first()
    if not user:
        return Response('user not found'), 404
    Contact.get_or_create(owner=current_user.id, contact=user.id)
    return Response('successful'), 200
