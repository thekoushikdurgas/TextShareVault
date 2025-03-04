from datetime import datetime
from app import db
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSONB

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    reputation = db.Column(db.Integer, default=0)
    achievements = db.Column(JSONB, default={})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    pastes = db.relationship('Paste', backref='author', lazy='dynamic')

class Paste(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paste_id = db.Column(db.String(16), unique=True, nullable=False)
    title = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(20), default='plaintext')
    images = db.Column(JSONB, default=[])
    is_deployed = db.Column(db.Boolean, default=False)
    deployment_url = db.Column(db.String(200))
    views = db.Column(db.Integer, default=0)
    stars = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tags = db.Column(JSONB, default=[])

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    icon = db.Column(db.String(50))
    points = db.Column(db.Integer, default=0)
    criteria = db.Column(JSONB)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
