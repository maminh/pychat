from celery import Celery
from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_sse import sse
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import CSRFProtect
from pymemcache.client import base

from local_params import MEM_CACHE_HOST
from .config import *

App = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
App.config.from_object(Config)
login = LoginManager()
socket_io = SocketIO(App)
mem_cache = base.Client((MEM_CACHE_HOST, 11211))


login.login_view = 'login'
login.init_app(App)

profiles = UploadSet('profiles', IMAGES)
configure_uploads(App, profiles)
patch_request_class(App)

App.register_blueprint(sse, url_prefix='/stream')
celery = Celery(App.import_name, broker=App.config['CELERY_BROKER_URL'])

csrf = CSRFProtect(App)

from .routes import *
