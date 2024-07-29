from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Like(db.Model):
    """Model for the likes table."""
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Dislike(db.Model):
    """Model for the dislikes table."""
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    """Model for the comments table."""
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(100), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class View(db.Model):
    """Model for the views table."""
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
