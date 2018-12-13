from flask import Flask
from flask_login import LoginManager
from flask_sse import sse

from .config import *

App = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
App.config.from_object(Config)
login = LoginManager()

login.login_view = 'login'
login.init_app(App)

App.register_blueprint(sse, url_prefix='/stream')

from .routes import *