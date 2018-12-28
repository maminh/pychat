from app import App
from .chat import *
from .contacts import *
from .room import *
from .user import *


@App.route('/')
@login_required
def index():
    return render_template("index.html", user=current_user, profile=current_user.profile)


@App.route('/chat_room/')
@login_required
def chat_room():
    return render_template('chat_room.html', user=current_user)
