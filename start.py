from flask_socketio import SocketIO

from app import App

from local_params import DEBUG_MODE, HOST


socketio = SocketIO()

if __name__ == '__main__':
    App.debug = DEBUG_MODE
    socketio.init_app(App,engineio_logger=True)
    socketio.run(App)
    # App.run(threaded=True, host=HOST)
