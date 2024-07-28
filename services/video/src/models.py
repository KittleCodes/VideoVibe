from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Video(db.Model):
    token = db.Column(db.String(200), primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500))
    author_id = db.Column(db.Integer, nullable=False)