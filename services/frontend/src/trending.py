from __main__ import app
import requests
import jwt
from flask import request, render_template_string

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

        return render_template_string('''
<!DOCTYPE html>
<html data-bs-theme="light" lang="en">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
    <title>VideoVibe</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootswatch@5.3.3/dist/darkly/bootstrap.min.css">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,400;0,700;1,400&amp;display=swap">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Almarai&amp;display=swap">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/geopattern/1.2.3/js/geopattern.min.js"></script>
    <script>
    window.jdenticon_config = {
        lightness: {
            color: [0.59, 0.80],
            grayscale: [0.59, 0.84]
        },
        saturation: {
            color: 1.00,
            grayscale: 0.45
        },
        backColor: "#0000"
    };
    </script>
    <script src="https://cdn.jsdelivr.net/npm/jdenticon@3.3.0/dist/jdenticon.min.js" 
        integrity="sha384-LfouGM03m83ArVtne1JPk926e3SGD0Tz8XHtW2OKGsgeBU/UfR0Fa8eX+UlwSSAZ" crossorigin="anonymous">
    </script>
</head>

<body>
    <nav class="navbar navbar-expand-md bg-dark py-3" data-bs-theme="dark">
        <div class="container"><a class="navbar-brand d-flex align-items-center" href="/"><span class="bs-icon-sm bs-icon-rounded bs-icon-primary d-flex justify-content-center align-items-center me-2 bs-icon"><svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" viewBox="0 0 16 16" class="bi bi-camera-video">
                        <path fill-rule="evenodd" d="M0 5a2 2 0 0 1 2-2h7.5a2 2 0 0 1 1.983 1.738l3.11-1.382A1 1 0 0 1 16 4.269v7.462a1 1 0 0 1-1.406.913l-3.111-1.382A2 2 0 0 1 9.5 13H2a2 2 0 0 1-2-2zm11.5 5.175 3.5 1.556V4.269l-3.5 1.556zM2 4a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h7.5a1 1 0 0 0 1-1V5a1 1 0 0 0-1-1z"></path>
                    </svg></span><span>VideoVibe</span></a><button data-bs-toggle="collapse" class="navbar-toggler" data-bs-target="#navcol-5"><span class="visually-hidden">Toggle navigation</span><span class="navbar-toggler-icon"></span></button>
            <div class="collapse navbar-collapse" id="navcol-5">
                <div class="d-inline-flex" style="width: 50%;margin-left: 0px;"><input class="d-xl-flex justify-content-xl-start align-items-xl-center" type="search" placeholder="Search.." name="search" style="margin-left: 0px;padding-top: 5px;padding-bottom: 5px;padding-right: 0px;width: 100%;border-style: none;border-radius: 5px;background: var(--bs-body-bg);padding-left: 10px;min-width: 200px;"><button class="btn btn-primary d-xl-flex justify-content-xl-end align-items-xl-center" type="button" style="margin-left: 10px;"><svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" viewBox="0 0 16 16" class="bi bi-search">
                            <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0"></path>
                        </svg></button></div>
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="/new">New</a></li>
                    <li class="nav-item"><a class="nav-link active" href="/trending">Trending</a></li>
                </ul>
                {% if logged_in != None: %}
                    <svg data-jdenticon-value="{{logged_in["username"]}}" width="35" height="35" style="margin-left: 10px;background-color: black;"></svg>
                {% else %}
                    <a class="btn btn-primary ms-md-2" role="button" href="/login" style="background: var(--bs-blue);width: 80.0375px;">Login</a>
                {% endif %}
            </div>
        </div>
    </nav>
    <div class="col" style="padding-left: 50px;padding-right: 50px;margin-top: 30px;">
        <h3 class="text-center">Today's Top 20 Trending Videos</h3>
        <div id="channelVideos" class="container">
            {% for video in videos %}
                <div id="videoTemplate" class="row mb-3">
                    <div class="col-12 d-flex justify-content-center">
                        <div class="card text-center" style="width: 100%; max-width: 600px;">
                            <div class="card-body">
                                <a href="/video/{{video.token}}">
                                    <img alt="" class="img-fluid" style="border-radius: 10px; max-height: 300px;" src="http://127.0.0.1:8000/video/dash/{{video.token}}/{{video.token}}.jpg">
                                </a>
                                <a href="/video/{{video.token}}"><h4 class="card-title mt-3">{{video.title}}</h4></a>
                            </div>
                        </div>
                    </div>
                </div>
            {% endfor %}
            {% if videos == {} %}
                <h4 class="text-center">No trending videos within the last day!</h4>
            {% endif %}
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>

</html>
''', videos=videos_response["videos"], logged_in=decoded)
    else:
        return 'Channel not found', 404
