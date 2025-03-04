import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import secrets
from utils.ai_analysis import analyze_content


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# configure the database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
# initialize the app with the extension, flask-sqlalchemy >= 3.0.x
db.init_app(app)

with app.app_context():
    # Make sure to import the models here or their tables won't be created
    import models  # noqa: F401

    db.create_all()

# Import routes after db initialization to avoid circular imports
from routes import register_routes
register_routes(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'user_id': request.sid})

@socketio.on('join')
def handle_join(data):
    """Handle client joining a paste room"""
    room = data['paste_id']
    username = data.get('username', f'User_{request.sid[:6]}')
    join_room(room)
    emit('user-join', {'user_id': request.sid, 'username': username}, room=room, include_self=False)

@socketio.on('text-change')
def handle_text_change(data):
    """Handle text changes in collaborative editing"""
    room = data['paste_id']
    emit('text-change', {'delta': data['delta'], 'user_id': request.sid}, room=room, include_self=False)

@socketio.on('cursor-move')
def handle_cursor_move(data):
    """Handle cursor movement updates"""
    room = data['paste_id']
    emit('cursor-move', {
        'range': data['range'],
        'user_id': request.sid,
        'username': f'User_{request.sid[:6]}'
    }, room=room, include_self=False)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    emit('user-leave', {'user_id': request.sid}, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)