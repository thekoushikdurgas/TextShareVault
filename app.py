import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from pymongo import MongoClient
import secrets
from utils.ai_analysis import analyze_content
from flask_socketio import SocketIO, emit, join_room, leave_room
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", secrets.token_hex(16))

# MongoDB Atlas setup
MONGODB_URI = "mongodb+srv://prbal:ImoYJiYRkJaMC8vF@thekoushikdurgas.nyx7d.mongodb.net/"
try:
    client = MongoClient(MONGODB_URI)
    # Test connection
    client.admin.command('ping')
    logger.info("Successfully connected to MongoDB Atlas")
    db = client.pastebin  # Use pastebin database
    pastes = db.Pattinson  # Use Pattinson collection
except Exception as e:
    logger.error(f"Failed to connect to MongoDB Atlas: {e}")
    raise

def get_recent_pastes():
    """Helper function to get recent pastes for the sidebar"""
    try:
        return list(pastes.find().sort("created_at", -1).limit(10))
    except Exception as e:
        logger.error(f"Failed to fetch recent pastes: {e}")
        return []

# Register the function as a template global
app.jinja_env.globals.update(get_recent_pastes=get_recent_pastes)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        content = request.form.get("content")
        title = request.form.get("title", "Untitled")
        language = request.form.get("language", "plaintext")
        images = request.form.getlist("images[]")  # Get list of image URLs

        if not content:
            flash("Content cannot be empty!", "error")
            return redirect(url_for("index"))

        try:
            paste_id = secrets.token_urlsafe(8)
            paste = {
                "paste_id": paste_id,
                "title": title,
                "content": content,
                "language": language,
                "images": images,
                "created_at": datetime.utcnow()
            }

            pastes.insert_one(paste)
            logger.debug(f"Successfully created paste with ID: {paste_id}")
            return redirect(url_for("view_paste", paste_id=paste_id))
        except Exception as e:
            logger.error(f"Failed to create paste: {e}")
            flash("Failed to create paste. Please try again.", "error")
            return redirect(url_for("index"))

    return render_template("index.html")

@app.route("/<paste_id>")
def view_paste(paste_id):
    try:
        paste = pastes.find_one({"paste_id": paste_id})
        if not paste:
            flash("Paste not found!", "error")
            return redirect(url_for("index"))

        return render_template("view.html", paste=paste)
    except Exception as e:
        logger.error(f"Failed to retrieve paste {paste_id}: {e}")
        flash("Failed to retrieve paste. Please try again.", "error")
        return redirect(url_for("index"))

@app.route("/<paste_id>/analyze", methods=["POST"])
def analyze_paste(paste_id):
    try:
        paste = pastes.find_one({"paste_id": paste_id})
        if not paste:
            return jsonify({"error": "Paste not found"}), 404

        # Get the first image URL if available
        image_url = paste.get("images", [None])[0]

        # Analyze content using AI
        analysis = analyze_content(paste["content"], image_url)
        return jsonify({"analysis": analysis})
    except Exception as e:
        logger.error(f"Failed to analyze paste {paste_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/analyze/preview", methods=["POST"])
def analyze_preview():
    try:
        data = request.get_json()
        content = data.get("content")
        image_url = data.get("image_url")
        model = data.get("model", "google/gemini-exp-1206:free")

        if not content:
            return jsonify({"error": "No content provided"}), 400

        analysis = analyze_content(content, image_url, model)
        return jsonify({"analysis": analysis})
    except Exception as e:
        logger.error(f"Failed to analyze preview: {e}")
        return jsonify({"error": str(e)}), 500

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