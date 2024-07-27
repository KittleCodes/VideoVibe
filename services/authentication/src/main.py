from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import requests
from models import User

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

USER_SERVICE_URL = 'http://localhost:5001/'

@app.route('/login', methods=['POST'])
def login():
    """Login and provide an access token."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    response = requests.get(f"{USER_SERVICE_URL}/find", timeout=5, params={"email": email})
    if response.status_code != 200:
        return jsonify(message='User not found'), 404

    user_data = response.json()
    user = User(**user_data)
    
    if bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify(message='Invalid credentials'), 401

@app.route('/verify', methods=['GET'])
@jwt_required()
def verify():
    """Verify the access token."""
    user_id = get_jwt_identity()
    return jsonify(user_id=user_id), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
