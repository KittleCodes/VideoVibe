from functools import wraps
from collections import defaultdict
import requests
from flask import Flask, request, jsonify, Response
from models import db, Keyword

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recommendation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

AUTH_SERVICE_URL = 'http://127.0.0.1:5000/'
VIDEO_SERVICE_URL = 'http://127.0.0.1:5002/'
SERVICE_TOKEN = 'my_secure_service_token' # Change this!

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

def require_service_auth(func):
    """Checks if the request is coming from an authorized service."""
    @wraps(func)
    def check_service_token(*args, **kwargs):
        if request.headers.get('X-Service-Token') != SERVICE_TOKEN:
            return Response("Access denied", status=403)
        return func(*args, **kwargs)

    return check_service_token

@app.route('/add_keywords', methods=['POST'])
@require_service_auth
def add_keywords():
    """Add new keywords for a video."""
    data = request.get_json()
    video_id = data.get('video_id')
    keywords = data.get('keywords')

    if not video_id or not keywords:
        return jsonify({"message": "Missing video_id or keywords"}), 400

    for word, count in keywords.items():
        keyword = Keyword(video_id=video_id, keyword=word, count=count)
        db.session.add(keyword)

    db.session.commit()

    return jsonify({"message": "Keywords added successfully"}), 201

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    """Get video recommendations based on keyword similarity."""
    data = request.get_json()
    video_id = data.get('video_id')
    amount = int(data.get('amount'))
    cursor = data.get('cursor')

    if not video_id:
        return jsonify({"message": "Missing video_id"}), 400

    base_keywords = db.session.query(Keyword.keyword, Keyword.count)\
        .filter(Keyword.video_id == video_id)\
        .all()

    if not base_keywords:
        return jsonify({"message": "No keywords found for the given video_id"}), 404

    base_keyword_dict = {keyword: count for keyword, count in base_keywords}

    other_videos = db.session.query(Keyword.video_id, Keyword.keyword, Keyword.count)\
        .filter(Keyword.video_id != video_id)\
        .all()

    video_scores = defaultdict(int)

    for vid, keyword, count in other_videos:
        if keyword in base_keyword_dict:
            video_scores[vid] += min(base_keyword_dict[keyword], count)

    filtered_scores = {vid: score for vid, score in video_scores.items() if cursor is None or score < cursor}

    sorted_videos = sorted(filtered_scores.items(), key=lambda x: x[1], reverse=True)

    top_videos = sorted_videos[:amount]

    next_cursor = top_videos[-1][1] if len(top_videos) == amount and len(sorted_videos) > amount else None

    recommendations = []
    for vid, score in top_videos:
        video_response = requests.get(f'{VIDEO_SERVICE_URL}/videos/{vid}')
        if video_response.status_code == 200:
            video_data = video_response.json()
            video_data['score'] = score
            recommendations.append(video_data)
        else:
            recommendations.append({"video_id": vid, "score": score, "message": "Video details not found"})
    response = {
        "recommendations": recommendations,
        "next_cursor": next_cursor
    }
    
    return jsonify(response)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5005, debug=True)
