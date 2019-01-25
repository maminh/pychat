import os

from app import App, socket_io
from app.models import User, Contact, Message, StreamModel , ChatVideos
from local_params import DEBUG_MODE, HOST

if not User.table_exists():
    User.create_table()

if not Contact.table_exists():
    Contact.create_table()

if not Message.table_exists():
    Message.create_table()

if not os.path.exists('media'):
    os.mkdir('media')

if not os.path.exists(os.path.join('media', 'profiles')):
    os.mkdir(os.path.join('media', 'profiles'))


if not StreamModel.table_exists():
    StreamModel.create_table()

if not ChatVideos.table_exists():
    ChatVideos.create_table()
if __name__ == '__main__':
    socket_io.run(App, host=HOST, debug=DEBUG_MODE, keyfile='key.pem', certfile='cert.pem')
