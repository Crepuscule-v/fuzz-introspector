from flask import render_template, Flask, request
from flask_socketio import SocketIO, emit 
from threading import Lock
import random

app = Flask(__name__)
socketio = SocketIO(app)
thread = None 
thread_lock = Lock()

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread == None:
            thread = socketio.start_background_task(target = background_thread)

def background_thread():
    while True:
        socketio.sleep(2)
        t = random.randint(1, 100)
        socketio.emit('server_response', {'data' : t}, namespace = '/test')

@socketio.on('message', namespace='/chat')
def handle_chat_message(data):
    print('Chat message:', data)

@socketio.on('client_connected', namespace='/chat')
def handle_chat_message(data):
    print('Chat server connected:', data)


@socketio.on('move', namespace='/game')
def handle_game_move(data):
    print('Game move:', data)

# @app.route('/chat')
# def chat():
#     return render_template('chat.html')

if __name__ == '__main__':
    socketio.run(app)