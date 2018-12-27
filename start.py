import os

from app import App, socket_io
from app.models import User
from local_params import DEBUG_MODE, HOST

if not User.table_exists():
    User.create_table()

if not os.path.exists('media'):
    os.mkdir('media')

if not os.path.exists(os.path.join('media', 'profiles')):
    os.mkdir(os.path.join('media', 'profiles'))

if __name__ == '__main__':
    socket_io.run(App, host=HOST, debug=DEBUG_MODE)
