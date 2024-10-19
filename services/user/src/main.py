import hashlib
from functools import wraps
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from models import db, User

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bcrypt = Bcrypt(app)

db.init_app(app)


SERVICE_TOKEN = 'my_secure_service_token' # Change this!

def require_service_auth(func):
    """Checks if the request is coming from an authorized service."""
    @wraps(func)
    def check_service_token(*args, **kwargs):
        if request.headers.get('X-Service-Token') != SERVICE_TOKEN:
            return Response("Access denied", status=403)
        return func(*args, **kwargs)

    return check_service_token

def email_to_unique_username(email, word_count=4):
    with open("top-1000-nouns.txt", 'r') as file:
        word_list = [line.strip() for line in file.readlines()]
    email_hash = hashlib.sha256(email.encode()).hexdigest()

    number = int(email_hash, 16)

    words = []
    
    for i in range(word_count):
        word_index = number % len(word_list)
        words.append(word_list[word_index].capitalize())
        number //= len(word_list)

    return "".join(words)

@app.route('/pfp/<path:path>')
def send_pfp(path):
    return send_from_directory('pfp', path)

@app.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()

    if data is None:
        return jsonify(message='No input data provided!'), 400

    if 'email' not in data or 'password' not in data:
        return jsonify(message='Missing email or password!'), 400

    user = User.query.filter_by(email=data['email']).first()
    
    if user:
        return jsonify(message='Email already in use!'), 400
    else:
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(username=email_to_unique_username(email=data['email']), email=data['email'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify(message='User registered successfully'), 201

@app.route('/find', methods=['GET'])
@require_service_auth
def find_user():
    """Find a user by email."""
    email = request.args.get('email')
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify(id=user.id, username = user.username, email=user.email, password=user.password), 200
    else:
        return jsonify(message='User not found'), 404

@app.route('/findusername', methods=['GET'])
def find_username():
    """Find usernames by ids."""
    ids = request.args.getlist('id')
    users = User.query.filter(User.id.in_(ids)).all()
    
    if users:
        return jsonify([{ 'id': user.id, 'username': user.username } for user in users]), 200
    else:
        return jsonify(message='No users found'), 404

@app.route('/profile', methods=['GET'])
def profile():
    """Get a user profile."""
    user_id = request.args.get('id')
    user = User.query.get(user_id)
    if user:
        return jsonify(id=user.id, email=user.email), 200
    else:
        return jsonify(message='User not found'), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5001, debug=True)
