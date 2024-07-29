from functools import wraps
import requests
from flask import Flask, request, jsonify, Response
from models import db, Keyword

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recommendation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

AUTH_SERVICE_URL = 'http://localhost:5000/'
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5005, debug=True)
