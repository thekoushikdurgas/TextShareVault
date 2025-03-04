from flask import render_template, request, redirect, url_for, flash, jsonify
from models import User, Paste, Achievement
from utils.ai_analysis import analyze_content
from services.achievement_service import AchievementService
from services.deployment_service import DeploymentService
from sqlalchemy import or_
import secrets
from datetime import datetime

def register_routes(app):
    def get_recent_pastes():
        """Helper function to get recent pastes for the sidebar"""
        try:
            return Paste.query.order_by(Paste.created_at.desc()).limit(10).all()
        except Exception as e:
            app.logger.error(f"Failed to fetch recent pastes: {e}")
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
                paste = Paste(
                    paste_id=paste_id,
                    title=title,
                    content=content,
                    language=language,
                    images=images,
                    created_at=datetime.utcnow()
                )
                app.config['db'].session.add(paste)
                app.config['db'].session.commit()
                return redirect(url_for("view_paste", paste_id=paste_id))
            except Exception as e:
                app.logger.error(f"Failed to create paste: {e}")
                flash("Failed to create paste. Please try again.", "error")
                return redirect(url_for("index"))

        return render_template("index.html")

    @app.route("/<paste_id>")
    def view_paste(paste_id):
        try:
            paste = Paste.query.filter_by(paste_id=paste_id).first()
            if not paste:
                flash("Paste not found!", "error")
                return redirect(url_for("index"))

            return render_template("view.html", paste=paste)
        except Exception as e:
            app.logger.error(f"Failed to retrieve paste {paste_id}: {e}")
            flash("Failed to retrieve paste. Please try again.", "error")
            return redirect(url_for("index"))

    @app.route("/<paste_id>/analyze", methods=["POST"])
    def analyze_paste(paste_id):
        try:
            paste = Paste.query.filter_by(paste_id=paste_id).first()
            if not paste:
                return jsonify({"error": "Paste not found"}), 404

            image_url = paste.images[0] if paste.images else None
            analysis = analyze_content(paste.content, image_url)
            return jsonify({"analysis": analysis})
        except Exception as e:
            app.logger.error(f"Failed to analyze paste {paste_id}: {e}")
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
            app.logger.error(f"Failed to analyze preview: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/<paste_id>/deploy', methods=['POST'])
    def deploy_paste(paste_id):
        try:
            deployment_url = DeploymentService.deploy_paste(paste_id)
            return jsonify({
                'success': True,
                'deployment_url': deployment_url
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/search', methods=['GET'])
    def search_pastes():
        query = request.args.get('q', '')
        language = request.args.get('language')
        sort_by = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')

        paste_query = Paste.query

        if query:
            paste_query = paste_query.filter(
                or_(
                    Paste.title.ilike(f'%{query}%'),
                    Paste.content.ilike(f'%{query}%'),
                    Paste.tags.contains([query])
                )
            )

        if language:
            paste_query = paste_query.filter(Paste.language == language)

        if order == 'desc':
            paste_query = paste_query.order_by(getattr(Paste, sort_by).desc())
        else:
            paste_query = paste_query.order_by(getattr(Paste, sort_by).asc())

        pastes = paste_query.all()

        return render_template(
            'search.html',
            pastes=pastes,
            query=query,
            language=language,
            sort_by=sort_by,
            order=order
        )

    @app.route('/user/<username>')
    def user_profile(username):
        user = User.query.filter_by(username=username).first_or_404()
        achievements = Achievement.query.all()

        return render_template(
            'profile.html',
            user=user,
            achievements=achievements
        )

    return app