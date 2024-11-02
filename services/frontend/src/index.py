from __main__ import app
from flask import request, render_template
import jwt

@app.route('/')
def index():
    token = request.cookies.get('access_token')
    decoded = None
    if token:
        decoded = jwt.decode(token, options={"verify_signature": False})
    
    return render_template('index.html', logged_in=decoded)
