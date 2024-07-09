from app import socketio
from flask_socketio import send, emit
from flask_login import current_user

@socketio.on('message')
def handle_message(msg):
    """
    Handle incoming messages and broadcast to all connected clients.
    """
    if current_user.is_authenticated:
        send({'msg': f'{current_user.username}: {msg}'}, broadcast=True)
    else:
        send({'msg': f'Guest: {msg}'}, broadcast=True)

@socketio.on('custom_event')
def handle_custom_event(json):
    """
    Handle custom events and broadcast the data.
    """
    if current_user.is_authenticated:
        emit('response', {'data': f'{current_user.username} says: {json}'}, broadcast=True)
    else:
        emit('response', {'data': f'Guest says: {json}'}, broadcast=True)
