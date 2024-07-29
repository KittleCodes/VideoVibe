from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Keyword(db.Model):
    """Model for the keywords table."""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    video_id = db.Column(db.String(100), nullable=False)
    keyword = db.Column(db.String, nullable=False)
    count = db.Column(db.Integer, nullable=False)
