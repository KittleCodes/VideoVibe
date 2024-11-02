from __main__ import app
import requests
import jwt
from flask import request, render_template

ENGAGEMENT_SERVICE_URL = 'http://127.0.0.1:5003'

@app.route('/trending', methods=['GET'])
def top_trending():
    """Get the trending videos of today."""
    videos_response = requests.get(f"{ENGAGEMENT_SERVICE_URL}/trending/20", timeout=10).json()
    if videos_response:
        token = request.cookies.get('access_token')
        decoded = None
        if token:
            decoded = jwt.decode(token, options={"verify_signature": False})

        return render_template('trending.html', videos=videos_response["videos"], logged_in=decoded)
    else:
        return 'Channel not found', 404
