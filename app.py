import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
import secrets

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

@app.route("/<paste_id>/edit", methods=["GET", "POST"])
def edit_paste(paste_id):
    try:
        paste = pastes.find_one({"paste_id": paste_id})
        if not paste:
            flash("Paste not found!", "error")
            return redirect(url_for("index"))

        if request.method == "POST":
            title = request.form.get("title", "Untitled")
            content = request.form.get("content")
            language = request.form.get("language", "plaintext")

            if not content:
                flash("Content cannot be empty!", "error")
                return redirect(url_for("edit_paste", paste_id=paste_id))

            pastes.update_one(
                {"paste_id": paste_id},
                {
                    "$set": {
                        "title": title,
                        "content": content,
                        "language": language,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            flash("Paste updated successfully!", "success")
            return redirect(url_for("view_paste", paste_id=paste_id))

        return render_template("edit.html", paste=paste)
    except Exception as e:
        logger.error(f"Failed to edit paste {paste_id}: {e}")
        flash("Failed to edit paste. Please try again.", "error")
        return redirect(url_for("index"))

@app.route("/<paste_id>/delete", methods=["POST"])
def delete_paste(paste_id):
    try:
        result = pastes.delete_one({"paste_id": paste_id})
        if result.deleted_count:
            flash("Paste deleted successfully!", "success")
        else:
            flash("Paste not found!", "error")
    except Exception as e:
        logger.error(f"Failed to delete paste {paste_id}: {e}")
        flash("Failed to delete paste. Please try again.", "error")

    return redirect(url_for("index"))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("index.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("index.html"), 500