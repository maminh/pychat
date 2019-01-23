from app import App
from app.models import User
from local_params import DEBUG_MODE, HOST

if not User.table_exists():
    User.create_table()
if __name__ == '__main__':
    App.debug = DEBUG_MODE
    App.run(threaded=True, host=HOST)
