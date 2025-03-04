import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
import secrets

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", secrets.token_hex(16))

# MongoDB setup
client = MongoClient(os.environ.get("MONGODB_URI", "mongodb://localhost:27017/"))
db = client.pastebin
pastes = db.pastes

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        content = request.form.get("content")
        title = request.form.get("title", "Untitled")
        language = request.form.get("language", "plaintext")
        
        if not content:
            flash("Content cannot be empty!", "error")
            return redirect(url_for("index"))

        paste_id = secrets.token_urlsafe(8)
        paste = {
            "paste_id": paste_id,
            "title": title,
            "content": content,
            "language": language,
            "created_at": datetime.utcnow()
        }
        
        pastes.insert_one(paste)
        return redirect(url_for("view_paste", paste_id=paste_id))
    
    return render_template("index.html")

@app.route("/<paste_id>")
def view_paste(paste_id):
    paste = pastes.find_one({"paste_id": paste_id})
    if not paste:
        flash("Paste not found!", "error")
        return redirect(url_for("index"))
    
    return render_template("view.html", paste=paste)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("index.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("index.html"), 500
