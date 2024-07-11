# app/socketio_events.py

from app import socketio
from flask_socketio import emit
from flask_login import current_user

@socketio.on('connect')
def handle_connect():
    """
    Handle user connection.
    """
    if current_user.is_authenticated:
        emit('message', {'data': f'User {current_user.username} connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """
    Handle user disconnection.
    """
    if current_user.is_authenticated:
        emit('message', {'data': f'User {current_user.username} disconnected'})

@socketio.on('notification')
def handle_notification(data):
    """
    Handle sending notifications to users.
    """
    emit('notification', {'data': data}, broadcast=True)
