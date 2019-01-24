from app import App
from app.models import User, StreamModel , ChatVideos
from local_params import DEBUG_MODE, HOST

if not User.table_exists():
    User.create_table()

if not StreamModel.table_exists():
    StreamModel.create_table()

if not ChatVideos.table_exists():
    ChatVideos.create_table()
if __name__ == '__main__':
    App.debug = DEBUG_MODE
    App.run(threaded=True, host=HOST)
