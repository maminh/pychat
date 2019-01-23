from app import App
from app.models import *

from local_params import DEBUG_MODE, HOST


if __name__ == '__main__':
    User.create_table()
    Contact.create_table()
    App.debug = DEBUG_MODE
    App.run(threaded=True, host=HOST)
