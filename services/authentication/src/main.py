import datetime
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import requests
from models import User

app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=30)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

USER_SERVICE_URL = 'http://127.0.0.1:5001/'
SERVICE_TOKEN = 'my_secure_service_token' # Change this!

@app.route('/login', methods=['POST'])
def login():
    """Login and provide an access token."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    response = requests.get(f"{USER_SERVICE_URL}/find", timeout=5, params={"email": email}, headers={"X-Service-Token": SERVICE_TOKEN})
    if response.status_code != 200:
        return jsonify(message='User not found'), 404

    user_data = response.json()
    user = User(**user_data)
    
    if bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(
            identity=user.id,
            additional_claims={"username": user.username}
        )
        resp = make_response(jsonify(access_token=access_token))
        resp.set_cookie("access_token", value=access_token)
        return resp, 200
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
