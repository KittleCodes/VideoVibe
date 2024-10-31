import os
import json
import requests
import datetime
from functools import wraps
from flask import Flask, request, jsonify, Response
from models import db, Like, Dislike, Comment, View, Subscription
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///engagement.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

USER_SERVICE_URL = 'http://127.0.0.1:5001/'
AUTH_SERVICE_URL = 'http://127.0.0.1:5000/'
VIDEO_SERVICE_URL = 'http://127.0.0.1:5002/'

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

@app.route('/comments', methods=['GET'])
def get_comments():
    """Get paginated comments for a video using timestamp-based cursor pagination."""
    video_id = request.args.get('video_id')
    last_timestamp = request.args.get('last_timestamp')
    print(last_timestamp)
    per_page = 20

    query = Comment.query.filter_by(video_id=video_id).order_by(Comment.timestamp)
    count = db.session.query(func.count(Comment.id)).filter(Comment.video_id == video_id).scalar()
    
    if last_timestamp != None:
        query = query.filter(Comment.timestamp > last_timestamp)

    comments = query.limit(per_page).all()
    
    user_ids = [comment.user_id for comment in comments]
    response = requests.get(f"{USER_SERVICE_URL}/findusername", timeout=5, params={"id": user_ids})

    usernames = {user['id']: user['username'] for user in response.json()} if response.status_code == 200 else {}

    newComments = []

    for comment in comments:
        comment_dict = comment.to_dict()
        comment_dict['username'] = usernames.get(int(comment.user_id), "Unknown")
        newComments.append(comment_dict)

    return jsonify({
        "comments": newComments,
        "commentCount": count,
        "last_timestamp": comments[-1].timestamp.isoformat() if comments else None,
        "has_more": len(comments) == per_page
    })

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

@app.route('/subscribe', methods=['POST'])
@require_auth
def subscribe_user(user_id):
    """Subscribe to a user."""
    subscribe_to_id = request.json.get('subscribe_to_id')

    if user_id == subscribe_to_id:
        return jsonify({"message": "You cannot subscribe to yourself"}), 400

    existing_subscription = Subscription.query.filter_by(subscriber_id=user_id, subscribed_to_id=subscribe_to_id).first()
    if existing_subscription:
        return jsonify({"message": "You are already subscribed to this user"}), 400

    subscription = Subscription(subscriber_id=user_id, subscribed_to_id=subscribe_to_id)
    db.session.add(subscription)
    db.session.commit()

    subscriptions_count = Subscription.query.filter_by(subscriber_id=user_id).count()
    return jsonify({"message": "Subscription added", "subscriptions": subscriptions_count})

@app.route('/unsubscribe', methods=['POST'])
@require_auth
def unsubscribe_user(user_id):
    """Unsubscribe from a user."""
    unsubscribe_from_id = request.json.get('unsubscribe_from_id')

    subscription = Subscription.query.filter_by(subscriber_id=user_id, subscribed_to_id=unsubscribe_from_id).first()
    if not subscription:
        return jsonify({"message": "You are not subscribed to this user"}), 400

    db.session.delete(subscription)
    db.session.commit()

    subscriptions_count = Subscription.query.filter_by(subscriber_id=user_id).count()
    return jsonify({"message": "Subscription removed", "subscriptions": subscriptions_count})

@app.route('/trending/<int:amount>')
def trending(amount):
    """Get the 20 most trending videos."""
    amount = amount if amount >= 20 else 20
    
    videos = (db.session.query(View.video_id, func.count(View.id).label("view_count"))
        .filter(View.timestamp >= (datetime.datetime.utcnow() - datetime.timedelta(days=1)))
        .group_by(View.video_id)
        .order_by(func.count(View.id).desc())
        .limit(amount)
        .all()
    )
    
    new_videos = {}
    
    for video in videos:
        video_request = requests.get(f'{VIDEO_SERVICE_URL}/videos/{video.video_id}')
        if video_request.status_code == 200:
            videos.append(video_request.json)
    
    return jsonify(videos=new_videos), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5003, debug=True)
