import os
import requests
from functools import wraps
from flask import Flask, request, jsonify, Response
from models import db, Like, Dislike, Comment, View

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///engagement.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

AUTH_SERVICE_URL = 'http://localhost:5000/'

def require_auth(func):
    """Checks if the request has a valid access token."""
    @wraps(func)
    def check_token(*args, **kwargs):
        if 'Authorization' not in request.headers:
            return Response("Access denied", status=401)

        try:
            response = requests.get(f'{AUTH_SERVICE_URL}/verify', headers={'Authorization': request.headers['Authorization']}, timeout=10).json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while verifying the token: {e}")
            return Response("Access denied", status=401)

        if 'user_id' not in response:
            return Response("Access denied", status=401)

        kwargs['user_id'] = response['user_id']

        return func(*args, **kwargs)

    return check_token

@app.route('/like', methods=['POST'])
@require_auth
def like_video(user_id):
    """Like a video."""
    video_id = request.json.get('video_id')

    existing_dislike = Dislike.query.filter_by(video_id=video_id, user_id=user_id).first()
    if existing_dislike:
        db.session.delete(existing_dislike)

    existing_like = Like.query.filter_by(video_id=video_id, user_id=user_id).first()
    if existing_like:
        return jsonify({"message": "You have already liked this video"}), 400

    like = Like(video_id=video_id, user_id=user_id)
    db.session.add(like)
    db.session.commit()

    return jsonify({"message": "Video liked", "likes": Like.query.filter_by(video_id=video_id).count()})


@app.route('/dislike', methods=['POST'])
@require_auth
def dislike_video(user_id):
    """Dislike a video."""
    video_id = request.json.get('video_id')

    existing_like = Like.query.filter_by(video_id=video_id, user_id=user_id).first()
    if existing_like:
        db.session.delete(existing_like)

    existing_dislike = Dislike.query.filter_by(video_id=video_id, user_id=user_id).first()
    if existing_dislike:
        return jsonify({"message": "You have already disliked this video"}), 400

    dislike = Dislike(video_id=video_id, user_id=user_id)
    db.session.add(dislike)
    db.session.commit()

    return jsonify({"message": "Video disliked", "dislikes": Dislike.query.filter_by(video_id=video_id).count()})


@app.route('/comment', methods=['POST'])
@require_auth
def comment_video(user_id):
    """Comment on a video."""
    video_id = request.json.get('video_id')
    comment_text = request.json.get('comment')

    comment = Comment(video_id=video_id, user_id=user_id, comment_text=comment_text)
    db.session.add(comment)
    db.session.commit()

    return jsonify({"message": "Comment added", "comments": [c.comment_text for c in Comment.query.filter_by(video_id=video_id).all()]})

@app.route('/view', methods=['POST'])
@require_auth
def view_video(user_id):
    """View a video."""
    video_id = request.json.get('video_id')

    existing_view = View.query.filter_by(video_id=video_id, user_id=user_id).first()
    if existing_view:
        return jsonify({"message": "You have already viewed this video"}), 400

    view = View(video_id=video_id, user_id=user_id)
    db.session.add(view)
    db.session.commit()

    return jsonify({"message": "Video viewed", "views": View.query.filter_by(video_id=video_id).count()})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5003, debug=True)
