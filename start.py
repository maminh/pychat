from app import App

from local_params import DEBUG_MODE, HOST


if __name__ == '__main__':
    App.debug = DEBUG_MODE
    App.run(threaded=True, host=HOST)
