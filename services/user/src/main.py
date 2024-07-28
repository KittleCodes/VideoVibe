from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bcrypt = Bcrypt(app)

db.init_app(app)

@app.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(message='User registered successfully'), 201

@app.route('/find', methods=['GET'])
def find_user():
    """Find a user by email."""
    email = request.args.get('email')
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify(id=user.id, email=user.email, password=user.password), 200
    else:
        return jsonify(message='User not found'), 404

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
