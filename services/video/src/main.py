import os
import secrets
from functools import wraps
import requests
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from models import db, Video
from werkzeug.utils import secure_filename
from video_processing import process_video
from transcribe import transcribe_and_save

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['DASH_FOLDER'] = 'dash/'

db.init_app(app)

CORS(app, resources={r"/*": {"origins": "http://127.0.0.1"}})

AUTH_SERVICE_URL = 'http://127.0.0.1:5000'
RECOMMENDATION_SERVICE_URL = 'http://127.0.0.1:5005'
CHANNEL_SERVICE_URL = 'http://127.0.0.1:5006'
SERVICE_TOKEN = 'my_secure_service_token' # Change this!
ID_LENGTH = 12
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi'}

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@app.route('/videos', methods=['POST'])
@require_auth
def create_video(user_id):
    """Create a new video."""
    channel_id = request.form.get('channel_id')

    # Verify that the user owns the channel
    try:
        channel_response = requests.get(f"{CHANNEL_SERVICE_URL}/find?id={channel_id}", timeout=10).json()
        print(channel_response)
        if 'message' in channel_response:  # Check if the channel was found
            return jsonify({'error': 'Channel not found'}), 404
        
        # Assuming the channel object includes user_id or owner_id
        if channel_response.get('user_id') != user_id:  # Check if the user_id matches
            return jsonify({'error': 'User does not own the specified channel'}), 403
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while checking channel ownership: {e}")
        return jsonify({'error': 'Error checking channel ownership'}), 500

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        file_ext = os.path.splitext(file.filename)[1]
        token = secrets.token_urlsafe(ID_LENGTH)
        filename = token + file_ext
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            keywords = transcribe_and_save(file_path)
        except Exception as error:
            print(f"An error occurred while transcribing the video: {error}")
            return jsonify({'error': 'An error occurred while transcribing the video'}), 500

        try:
            process_video(file_path, filename)
        except Exception as error:
            print(f"An error occurred while processing the video: {error}")
            return jsonify({'error': 'An error occurred while processing the video'}), 500

        try:
            requests.post(f"{RECOMMENDATION_SERVICE_URL}/add_keywords", json={"video_id": token, "keywords": keywords}, headers={"Content-Type": "application/json", "X-Service-Token": SERVICE_TOKEN}, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while sending keywords to the recommendation service: {e}")
            return jsonify({'error': 'An error occurred while sending keywords to the recommendation service'}), 500

        # Use channel_id as the author_id
        new_video = Video(title=filename, description=filename, token=token, author_id=channel_id)
        db.session.add(new_video)
        db.session.commit()

        return jsonify({'message': 'File uploaded and processed successfully'}), 200
    else:
        return jsonify({'error': 'Invalid file format'}), 400

@app.route('/videos/<token>', methods=['GET'])
def get_video(token):
    """Get a video by token."""
    video = Video.query.get(token)
    if video:
        channel_response = requests.get(f"{CHANNEL_SERVICE_URL}/find?id={video.author_id}", timeout=10).json()
        
        if channel_response:
            name = channel_response.get('name')
            username = channel_response.get('username')
            return jsonify(token=video.token, title=video.title, description=video.description, author_id=video.author_id, username=username, name=name), 200
        else:
            return jsonify({'error': 'Channel not found'}), 404
    else:
        return jsonify(message='Video not found'), 404

@app.route('/videos/<token>', methods=['PUT'])
@require_auth
def update_video(token, user_id):
    """Update a video by token."""
    data = request.get_json()
    channel_id = data.get('channel_id')
    video = Video.query.get(token)

    if video:
        # Check if the channel belongs to the user
        try:
            channel_response = requests.get(f"{AUTH_SERVICE_URL}/find?id={channel_id}", timeout=10).json()
            if 'message' in channel_response:  # Check if the channel was found
                return jsonify({'error': 'Channel not found'}), 404

            if channel_response.get('user_id') != user_id:  # Check if the user_id matches
                return jsonify(message='Unauthorized'), 403

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while checking channel ownership: {e}")
            return jsonify({'error': 'Error checking channel ownership'}), 500

        video.title = data.get('title', video.title)
        video.description = data.get('description', video.description)
        db.session.commit()
        return jsonify(token=video.token, title=video.title, description=video.description), 200
    else:
        return jsonify(message='Video not found'), 404

@app.route('/videos/<token>', methods=['DELETE'])
@require_auth
def delete_video(token, user_id):
    """Delete a video by token."""
    channel_id = request.args.get('channel_id')
    video = Video.query.get(token)

    if video:
        # Check if the channel belongs to the user
        try:
            channel_response = requests.get(f"{AUTH_SERVICE_URL}/find?id={channel_id}", timeout=10).json()
            if 'message' in channel_response:  # Check if the channel was found
                return jsonify({'error': 'Channel not found'}), 404

            if channel_response.get('user_id') != user_id:  # Check if the user_id matches
                return jsonify(message='Unauthorized'), 403

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while checking channel ownership: {e}")
            return jsonify({'error': 'Error checking channel ownership'}), 500

        db.session.delete(video)
        db.session.commit()
        return jsonify(message='Video deleted'), 200
    else:
        return jsonify(message='Video not found'), 404

@app.route('/uploads/<filename>')
def serve_upload(filename):
    """Serve video files from the uploads folder."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/dash/<path:filename>')
def serve_dash(filename):
    """Serve DASH files from the dash folder."""
    return send_from_directory(app.config['DASH_FOLDER'], filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5002, debug=True)
