from __main__ import app
import requests
import jwt
from flask import request, render_template

CHANNEL_SERVICE_URL = 'http://127.0.0.1:5006'

@app.route('/channel/<channel_id>', methods=['GET'])
def channel(channel_id):
    """Get a channel by id."""
    channel_response = requests.get(f"{CHANNEL_SERVICE_URL}/find?id={channel_id}", timeout=10).json()
    if channel_response:
        token = request.cookies.get('access_token')
        decoded = None
        if token:
            decoded = jwt.decode(token, options={"verify_signature": False})

        return render_template('channel.html', channel_data=channel_response, logged_in=decoded)
    else:
        return 'Channel not found', 404
