from app import App
from .room import *
from .user import *


@App.route('/')
@login_required
def index():
    return render_template("index.html", user=current_user)
