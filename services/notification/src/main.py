from functools import wraps
import requests
from flask import Flask, request, jsonify, Response
from models import db, Notification

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notifications.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

AUTH_SERVICE_URL = 'http://127.0.0.1:5000/'
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

@app.route('/add_notification', methods=['POST'])
@require_service_auth
def add_notification():
    """Add a new notification."""
    data = request.get_json()
    user_id = data.get('user_id')
    message = data.get('message')
    url = data.get('url')

    if not message:
        return jsonify({"error": "Username and message are required"}), 400

    notification = Notification(user_id=user_id, message=message, url=url)
    db.session.add(notification)
    db.session.commit()

    return jsonify({"message": "Notification added successfully"}), 201

@app.route('/notifications', methods=['GET'])
@require_auth
def get_notifications(user_id):
    """Get all notifications for a user."""
    notifications = Notification.query.filter_by(user_id=user_id).all()
    notifications_list = [
        {
            "id": notif.id,
            "message": notif.message,
            "url": notif.url,
            "timestamp": notif.timestamp,
            "is_read": notif.is_read
        } for notif in notifications
    ]
    return jsonify(notifications_list), 200

@app.route('/read_notification/<int:notification_id>', methods=['PUT'])
@require_auth
def read_notification(notification_id, user_id):
    notification = Notification.query.get(notification_id)
    if notification and notification.user_id == int(user_id):
        notification.is_read = True
        db.session.commit()
        return jsonify({"message": "Notification marked as read"}), 200
    elif notification:
        return jsonify({"error": "Unauthorized access to this notification"}), 403
    else:
        return jsonify({"error": "Notification not found"}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5004, debug=True)
