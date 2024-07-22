from flask import Flask
from flask_socketio import SocketIO

app = None
socketio = None

def create_app_socket():
    global app
    global socketio
    app = Flask(__name__)
    socketio = SocketIO(app, cors_allowed_origins='*')
    print(f'Created {app}')
    print(f'Created {socketio}')
    return app, socketio

def get_app_socket():
    print(f'Getting {app}')
    print(f'Getting {socketio}')
    return app, socketio