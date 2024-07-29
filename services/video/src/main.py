import os
import subprocess
import secrets
from functools import wraps
import subprocess
from concurrent.futures import ThreadPoolExecutor
import requests
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from models import db, Video
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['DASH_FOLDER'] = 'dash/'

db.init_app(app)

CORS(app)

AUTH_SERVICE_URL = 'http://localhost:5000/'
ID_LENGTH = 12
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi'}

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def run_ffmpeg_command(command, output_path):
    """Run an FFmpeg command and return the output."""
    process = subprocess.Popen(command, cwd=output_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg command failed with error: {stderr.decode('utf-8')}")
    return stdout, stderr

def process_video(file_path, filename):
    """Convert video to multi-bitrate in MPEG-DASH format."""
    file_path = os.path.abspath(file_path)  # Fullname of the file
    base_name = os.path.splitext(filename)[0]  # Name without extension
    
    dash_output_path = os.path.join(app.config['DASH_FOLDER'], base_name)
    os.makedirs(dash_output_path, exist_ok=True)

    if os.path.exists(dash_output_path):
        print(f"Converting \"{base_name}\" to multi-bitrate video in MPEG-DASH")

        try:
            # Extract audio streams
            audio_command_template = [
                'ffmpeg', '-y', '-i', file_path, '-map', '0:a:{stream_index}', 
                '-c:a', 'aac', '-b:a', '192k', '-vn', '{output_file}'
            ]
            audio_streams = []
            for i in range(10):  # Handle up to 10 audio streams
                output_file = f"{base_name}_audio_{i}.m4a"
                audio_command = [x.format(stream_index=i, output_file=output_file) for x in audio_command_template]
                try:
                    run_ffmpeg_command(audio_command, dash_output_path)
                    if os.path.exists(os.path.join(dash_output_path, output_file)):
                        audio_streams.append(output_file)
                except RuntimeError as e:
                    if "Stream map '0:a:" in str(e):
                        break  # No more audio streams available
                    else:
                        raise

            # Define video commands for different resolutions
            video_commands = [
                [
                    'ffmpeg', '-y', '-i', file_path, '-preset', 'medium', '-tune', 'film', '-vsync', 'passthrough',
                    '-an', '-c:v', 'libx264', '-x264opts', 'keyint=48:min-keyint=48:no-scenecut', '-crf', '22',
                    '-maxrate', '5000k', '-bufsize', '10000k', '-pix_fmt', 'yuv420p', '-f', 'mp4', f"{base_name}_original.mp4"
                ],
                [
                    'ffmpeg', '-y', '-i', file_path, '-preset', 'medium', '-tune', 'film', '-vsync', 'passthrough',
                    '-an', '-c:v', 'libx264', '-x264opts', 'keyint=48:min-keyint=48:no-scenecut', '-crf', '23',
                    '-maxrate', '3000k', '-bufsize', '6000k', '-pix_fmt', 'yuv420p', '-vf', 'scale=-2:720', '-f', 'mp4', f"{base_name}_720p.mp4"
                ],
                [
                    'ffmpeg', '-y', '-i', file_path, '-preset', 'medium', '-tune', 'film', '-vsync', 'passthrough',
                    '-an', '-c:v', 'libx264', '-x264opts', 'keyint=48:min-keyint=48:no-scenecut', '-crf', '23',
                    '-maxrate', '1500k', '-bufsize', '3000k', '-pix_fmt', 'yuv420p', '-vf', 'scale=-2:480', '-f', 'mp4', f"{base_name}_480p.mp4"
                ]
            ]

            with ThreadPoolExecutor() as executor:
                executor.map(lambda cmd: run_ffmpeg_command(cmd, dash_output_path), video_commands)

            # Generate DASH manifest
            dash_command = [
                'MP4Box', '-dash', '4000', '-rap', '-frag-rap', '-bs-switching', 'no', '-profile', 'dashavc264:live',
                f"{base_name}_original.mp4", f"{base_name}_720p.mp4", f"{base_name}_480p.mp4"
            ] + audio_streams + ['-out', f"{base_name}.mpd"]
            run_ffmpeg_command(dash_command, dash_output_path)

            # Clean up individual segments
            for file in [f"{base_name}_original.mp4", f"{base_name}_720p.mp4", f"{base_name}_480p.mp4"] + audio_streams:
                os.remove(os.path.join(dash_output_path, file))

            # Create a jpg for poster
            poster_command = [
                'ffmpeg', '-i', file_path, '-ss', '00:00:00', '-vframes', '1', '-qscale:v', '10', '-n', '-f', 'image2', f"{base_name}.jpg"
            ]
            run_ffmpeg_command(poster_command, dash_output_path)

        except Exception as e:
            print(f"An error occurred while processing the video: {e}")

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

        process_video(file_path, filename)

        new_video = Video(title=filename, description=filename, token=token, author_id=user_id)
        db.session.add(new_video)
        db.session.commit()

        return jsonify({'message': 'File uploaded and processed successfully'}), 200
    else:
        return jsonify({'error': 'Invalid file format'}), 400

@app.route('/videos/<token>', methods=['GET'])
@require_auth
def get_video(token, user_id):
    """Get a video by token."""
    video = Video.query.get(token)
    if video:
        return jsonify(token=video.token, title=video.title, description=video.description), 200
    else:
        return jsonify(message='Video not found'), 404

@app.route('/videos/<token>', methods=['PUT'])
@require_auth
def update_video(token, user_id):
    """Update a video by token."""
    data = request.get_json()
    video = Video.query.get(token)
    if video:
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
    video = Video.query.get(token)
    if video:
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
