from __main__ import app
from flask import request, render_template
import jwt

@app.route('/upload')
def upload():
   return render_template('upload.html')

@app.route('/video/<id>')
def video(id):
    token = request.cookies.get('access_token')
    decoded = None
    if token:
        decoded = jwt.decode(token, options={"verify_signature": False})
        
    return render_template('video.html', logged_in=decoded)