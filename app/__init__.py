from flask import Flask
from flask_login import LoginManager
from flask_sse import sse
from celery import Celery
from .config import *

App = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
App.config.from_object(Config)
login = LoginManager()

login.login_view = 'login'
login.init_app(App)

App.register_blueprint(sse, url_prefix='/stream')
celery = Celery(App.import_name,broker=App.config['CELERY_BROKER_URL'])

from .routes import *
