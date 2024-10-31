import requests
from functools import wraps
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from models import db, Channel

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bcrypt = Bcrypt(app)

db.init_app(app)

AUTH_SERVICE_URL = 'http://127.0.0.1:5000'

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

@app.route('/banner/<path:path>')
def send_banner(path):
    return send_from_directory('banner', path)

@app.route('/pfp/<path:path>')
def send_pfp(path):
    return send_from_directory('pfp', path)

@app.route('/register', methods=['POST'])
@require_auth
def register(user_id):
    """Register a new channel."""
    data = request.get_json()
    username = data.get('username').lower()
    
    existing_channel = Channel.query.filter_by(username=username).first()
    if existing_channel:
        return jsonify(message='Channel username already taken'), 400
    
    new_channel = Channel(creator_id=user_id, name=data['name'], username=username, about="Change your about in channel settings!")
    db.session.add(new_channel)
    db.session.commit()
    return jsonify(message='Channel created successfully'), 201

@app.route('/find', methods=['GET'])
def find_channel():
    """Find a channel by id."""
    id = request.args.get('id')
    channel = Channel.query.filter_by(id=id).first()
    if channel:
        return jsonify(id=channel.id, user_id=channel.creator_id, name=channel.name, username=channel.username, about=channel.about, created_at=channel.created_at), 200
    else:
        return jsonify(message='Channel not found'), 404

@app.route('/edit/about', methods=['POST'])
@require_auth
def edit_about(user_id):
    """Edit the about field of a channel."""
    data = request.get_json()
    channel_id = data.get('channel_id')
    about = data.get('about')

    channel = Channel.query.filter_by(id = channel_id, creator_id = user_id).first()
    
    if channel:
        if len(about) <= 500:
            channel.about = about
            db.session.commit()
            
            return jsonify(message='About updated succesfully'), 200
        else:
            return jsonify(message='About is too many characters long'), 404
    else:
        return jsonify(message='Channel not found or you do not have access to that channel'), 404

@app.route('/edit/name', methods=['POST'])
@require_auth
def edit_name(user_id):
    """Edit the name field of a channel."""
    data = request.get_json()
    channel_id = data.get('channel_id')
    name = data.get('name')

    channel = Channel.query.filter_by(id = channel_id, creator_id = user_id).first()
    
    if channel:
        if len(name) <= 150:
            channel.name = name
            db.session.commit()
            
            return jsonify(message='Name updated succesfully'), 200
        else:
            return jsonify(message='Name is too many characters long'), 404
    else:
        return jsonify(message='Channel not found or you do not have access to that channel'), 404

@app.route('/edit/username', methods=['POST'])
@require_auth
def edit_username(user_id):
    """Edit the username field of a channel."""
    data = request.get_json()
    channel_id = data.get('channel_id')
    username = data.get('username').lower()

    existing_channel = Channel.query.filter_by(username=username).first()
    if existing_channel:
        return jsonify(message='Channel username already taken'), 400

    channel = Channel.query.filter_by(id = channel_id, creator_id = user_id).first()
    
    if channel:
        if len(username) <= 150:
            channel.username = username
            db.session.commit()
            
            return jsonify(message='Username updated succesfully'), 200
        else:
            return jsonify(message='Username is too many characters long'), 404
    else:
        return jsonify(message='Channel not found or you do not have access to that channel'), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5006, debug=True)
