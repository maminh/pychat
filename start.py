from app import App

if __name__ == '__main__':
    App.debug = True
    App.run(threaded=True, host='0.0.0.0')
