from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_sse import sse
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class

from .config import *

App = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
App.config.from_object(Config)
login = LoginManager()
socket_io = SocketIO(App)

login.login_view = 'login'
login.init_app(App)

profiles = UploadSet('profiles', IMAGES)
configure_uploads(App, profiles)
patch_request_class(App)

App.register_blueprint(sse, url_prefix='/stream')

from .routes import *
