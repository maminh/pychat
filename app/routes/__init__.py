from .chat import *
from .chat import *
from .contacts import *
from .room import *
from .user import *


@App.route('/')
@login_required
def index():
    return render_template("index.html", user=current_user, profile=current_user.profile)

