from flask import Flask, request, jsonify
from flask_cors import CORS
import aiohttp
import asyncio
import time
import json

app = Flask(__name__)
CORS(app)

AUTH_SERVICE_URL = 'http://127.0.0.1:5000'
USER_SERVICE_URL = 'http://127.0.0.1:5001'
VIDEO_SERVICE_URL = 'http://127.0.0.1:5002'
ENGAGEMENT_SERVICE_URL = 'http://127.0.0.1:5003'
RECOMMENDATION_SERVICE_URL = 'http://127.0.0.1:5005'
CHANNEL_SERVICE_URL = 'http://127.0.0.1:5006'

async def fetch(session, url, method, headers, data, params):
    async with session.request(method, url, headers=headers, json=data, params=params) as resp:
        try:
            if resp.status == 200:
                content_type = resp.headers.get('Content-Type', '')
                
                if 'application/json' in content_type:
                    response_content = await resp.json()
                else:
                    response_content = await resp.read()
            else:
                response_content = await resp.text()

        except Exception as e:
            print(f"Error decoding response: {e}")
            response_content = None
            
        return response_content, resp.status, resp.headers


def flatten_headers(headers):
    flattened = {}
    for key, value in headers.items():
        if key in flattened:
            flattened[key] += ', ' + value
        else:
            flattened[key] = value
    return flattened

@app.route('/<service>/<path:path>', methods=['POST', 'GET'])
async def proxy(service, path):
    start_time = time.time()
    services = {
        'auth': AUTH_SERVICE_URL,
        'user': USER_SERVICE_URL,
        'video': VIDEO_SERVICE_URL,
        'engagement': ENGAGEMENT_SERVICE_URL,
        'recommendation': RECOMMENDATION_SERVICE_URL,
        'channel': CHANNEL_SERVICE_URL
    }

    if service not in services:
        return jsonify({"error": "Service not found"}), 404

    headers = {key: value for key, value in request.headers.items() if key.lower() != 'content-length'}
    data = request.get_json() if request.is_json else None

    print(f"Request data: {data}")

    async with aiohttp.ClientSession() as session:
        response_content, status_code, response_headers = await fetch(
            session,
            f"{services[service]}/{path}",
            request.method,
            headers,
            data,
            request.args
        )
        
    request_duration = time.time() - start_time
    print(f"Request duration for {service}/{path}: {request_duration:.2f} seconds")

    response_headers = flatten_headers(response_headers)

    if isinstance(response_content, dict):
        return jsonify(response_content), status_code, response_headers
    else:
        return response_content, status_code, response_headers

if __name__ == '__main__':
    app.run(port=8000, debug=True)
