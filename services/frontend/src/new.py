from __main__ import app
import requests
import jwt
from flask import request, render_template

VIDEO_SERVICE_URL = 'http://127.0.0.1:5002'

@app.route('/new', methods=['GET'])
def newest():
    """Get the newest videos of today."""
    videos_response = requests.get(f"{VIDEO_SERVICE_URL}/videos/new/20", timeout=10).json()
    if videos_response:
        token = request.cookies.get('access_token')
        decoded = None
        if token:
            decoded = jwt.decode(token, options={"verify_signature": False})

        return render_template('new.html', videos=videos_response["videos"], logged_in=decoded)
    else:
        return 'Channel not found', 404
