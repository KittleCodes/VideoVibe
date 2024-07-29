from flask import Flask, request, Response
import requests

app = Flask(__name__)

AUTH_SERVICE_URL = 'http://localhost:5000'
USER_SERVICE_URL = 'http://localhost:5001'
ENGAGEMENT_SERVICE_URL = 'http://localhost:5003'

def get_request_data():
    """Get the request data."""
    if request.is_json:
        return request.get_json()
    return None

@app.route('/auth/<path:path>', methods=['POST', 'GET'])
def proxy_auth(path):
    """Proxy requests to the authentication service."""
    headers = {key: value for key, value in request.headers}
    data = get_request_data()
    
    resp = requests.request(
        method=request.method,
        url=f"{AUTH_SERVICE_URL}/{path}",
        headers=headers,
        json=data,
        params=request.args,
        timeout=5
    )
    return (resp.content, resp.status_code, dict(resp.headers))

@app.route('/user/<path:path>', methods=['POST', 'GET'])
def proxy_user(path):
    """Proxy requests to the user service."""
    headers = {key: value for key, value in request.headers}
    data = get_request_data()
    
    resp = requests.request(
        method=request.method,
        url=f"{USER_SERVICE_URL}/{path}",
        headers=headers,
        json=data,
        params=request.args,
        timeout=5
    )
    return (resp.content, resp.status_code, dict(resp.headers))

@app.route('/engagement/<path:path>', methods=['POST', 'GET'])
def proxy_engagement(path):
    """Proxy requests to the user service."""
    headers = {key: value for key, value in request.headers}
    data = get_request_data()
    
    resp = requests.request(
        method=request.method,
        url=f"{ENGAGEMENT_SERVICE_URL}/{path}",
        headers=headers,
        json=data,
        params=request.args,
        timeout=5
    )
    return (resp.content, resp.status_code, dict(resp.headers))

if __name__ == '__main__':
    app.run(port=8000, debug=True)
