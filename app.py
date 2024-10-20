from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.init_app(app)

# Store users and chat history
users = {}
connected_users = set()  # Set to store currently connected users
chat_history = []  # List to store chat history

# Maximum number of messages to keep
MAX_MESSAGES = 250

class User(UserMixin):
    def __init__(self, username):
        self.username = username

    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(username):
    return users.get(username)

@app.route('/')
def index():
    return render_template('index.html', chat_history=chat_history)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    if username not in users:
        users[username] = User(username)
    login_user(users[username])
    return redirect(url_for('chat'))

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', username=current_user.username)

@socketio.on('connect')
def handle_connect():
    connected_users.add(current_user.username)  # Add user to the connected users set
    emit('user_list', list(connected_users), broadcast=True)  # Send updated user list to all clients
    emit('message', {'msg': f'{current_user.username} has entered the chat!'}, broadcast=True)
    # Send the last 250 messages to the newly connected user
    emit('chat_history', chat_history)

@socketio.on('disconnect')
def handle_disconnect():
    connected_users.remove(current_user.username)  # Remove user from connected users set
    emit('user_list', list(connected_users), broadcast=True)  # Send updated user list to all clients
    emit('message', {'msg': f'{current_user.username} has left the chat!'}, broadcast=True)

@socketio.on('message')
def handle_message(data):
    data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Add a timestamp
    chat_history.append(data)  # Save message to history
    emit('message', data, broadcast=True)
    
    username = data['username']
    msg = data['msg']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Create message object
    message = {'username': username, 'msg': msg, 'timestamp': timestamp}

    # Append to chat history and maintain the limit
    chat_history.append(message)
    if len(chat_history) > MAX_MESSAGES:
        chat_history.pop(0)  # Remove the oldest message

if __name__ == '__main__':
    #socketio.run(app)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
