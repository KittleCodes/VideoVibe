from __main__ import app
from flask import request
import jwt

@app.route('/upload')
def upload():
   return '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>VideoVibe</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
  </head>
  <body>
    <h1>Upload a Video</h1>
    <form action="http://127.0.0.1:8000/video/videos" method="POST" enctype="multipart/form-data">
        <label for="file">Select video file:</label>
        <input type="file" id="file" name="file" accept=".mp4, .mov, .avi" required>
        <button type="submit">Upload</button>
    </form>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
  </body>
</html>
'''

@app.route('/video/<id>')
def video(id):
    token = request.cookies.get('access_token')
    decoded = None
    if token:
        decoded = jwt.decode(token, options={"verify_signature": False})
    
    login_or_svg = (
        '<a class="btn btn-primary ms-md-2" role="button" href="/login" style="background: var(--bs-blue);width: 80.0375px;">Login</a>'
        if not decoded
        else f'<svg data-jdenticon-value="{decoded["username"]}" width="35" height="35" style="margin-left: 10px;"></svg>'
    )
        
    return f'''
<!DOCTYPE html>
<html data-bs-theme="light" lang="en">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
    <title>VideoVibe</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootswatch@5.3.3/dist/darkly/bootstrap.min.css">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,400;0,700;1,400&amp;display=swap">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Almarai&amp;display=swap">
    <script src="https://cdn.dashjs.org/latest/dash.all.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/jdenticon@3.3.0/dist/jdenticon.min.js" async
        integrity="sha384-LfouGM03m83ArVtne1JPk926e3SGD0Tz8XHtW2OKGsgeBU/UfR0Fa8eX+UlwSSAZ" crossorigin="anonymous">
    </script>
</head>

<body style="font-family: Almarai, sans-serif;">
    <nav class="navbar navbar-expand-md bg-dark py-3" data-bs-theme="dark">
        <div class="container">
            <a class="navbar-brand d-flex align-items-center" href="/">
                <span class="bs-icon-sm bs-icon-rounded bs-icon-primary d-flex justify-content-center align-items-center me-2 bs-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" viewBox="0 0 16 16" class="bi bi-camera-video">
                        <path fill-rule="evenodd" d="M0 5a2 2 0 0 1 2-2h7.5a2 2 0 0 1 1.983 1.738l3.11-1.382A1 1 0 0 1 16 4.269v7.462a1 1 0 0 1-1.406.913l-3.111-1.382A2 2 0 0 1 9.5 13H2a2 2 0 0 1-2-2zm11.5 5.175 3.5 1.556V4.269l-3.5 1.556zM2 4a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h7.5a1 1 0 0 0 1-1V5a1 1 0 0 0-1-1z"></path>
                    </svg>
                </span>
                <span>VideoVibe</span>
            </a>
            <button data-bs-toggle="collapse" class="navbar-toggler" data-bs-target="#navcol-5">
                <span class="visually-hidden">Toggle navigation</span>
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navcol-5">
                <div class="d-inline-flex" style="width: 50%;margin-left: 0px;"><input class="d-xl-flex justify-content-xl-start align-items-xl-center" type="search" placeholder="Search.." name="search" style="margin-left: 0px;padding-top: 5px;padding-bottom: 5px;padding-right: 0px;width: 100%;border-style: none;border-radius: 5px;background: var(--bs-body-bg);padding-left: 10px;min-width: 200px;"><button class="btn btn-primary d-xl-flex justify-content-xl-end align-items-xl-center" type="button" style="margin-left: 10px;"><svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" viewBox="0 0 16 16" class="bi bi-search">
                            <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0"></path>
                        </svg></button></div>
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link active" href="/">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="/new">New</a></li>
                    <li class="nav-item"><a class="nav-link" href="#">Trending</a></li>
                </ul>
                {login_or_svg}
            </div>
        </div>
    </nav>
    <div class="row" style="margin: 0;">
        <div class="col-xl-8">
            <video id="videoPlayer" data-dashjs-player style="aspect-ratio: 16 / 9;height: auto;width: 100%; margin: 20px; margin-bottom: 5px; margin-right: 0px;border-radius: 6px;"loop="true" autoplay="true" controls crossorigin="anonymous">
                <track label="English" kind="subtitles" srclang="en" src="http://127.0.0.1:8000/video/dash/{id}/{id}.vtt" default />
            </video>
            <div class="container" style="background-color: #121212; margin: 20px; margin-bottom: 5px; margin-right: 0px; margin-top: 0; border-radius: 10px;padding:20px;min-width:100%;">
                <p style="font-size: 32px;" id="videoTitle">Video title</p>
                <a href=""><p id="channelName"><img>Channel Name</p></a>
                <p id="videoDescription">This is an example description for an example video.</p>
            </div>
            <div class="container" id="commentsSection" style="background-color: #121212; margin: 20px; margin-bottom: 5px; margin-right: 0px; border-radius: 10px;padding:20px;min-width:100%;">
                <div style="display: flex; align-items: center; padding: 5px 0;">
                    <h3 style="margin: 0; padding: 0;">Comments</h3>
                    <p style="font-size: 22px; margin: 0; margin-left: 5px; color: #AAAAAA;" id="amountComments"></p>
                </div>
                <div class="row" id="commentTemplate" style="display:none;">
                    <div style="display: flex; align-items: center;">
                        <svg id="authorIcon" width="35" height="35"></svg>
                        <p style="font-size: 18px; margin: 0; margin-left: 10px;" id="author">Commenter Name</p>
                        <p style="font-size: 14px; margin: 0; margin-left: 10px; color: #AAAAAA; align-self: center;" id="timestamp">just now</p>
                    </div>
                    <p id="content" style="margin-left: 45px;">This is an example comment text.</p>
                </div>
                <div id="commentSpinner" class="spinner-border" role="status" style="margin-left: 10px;"></div>
                <p id="load-more" onclick="loadComments()" style="display:none;">Load More Comments</p>
            </div>
        </div>
        <div id="relatedVideos" class="col">
            <h3 style="width: 90%;margin: 0 auto;float: none;margin-top: 20px;">Related Videos</h3>
            <div id="relatedVideoTemplate" class="card" style="width: 90%;margin: 0 auto;float: none;margin-top: 20px;display: none;">
                <div class="card-body" style="border-radius: 6px;margin auto;">
                    <a href=""><img alt="" style="width: 100%;height: auto;border-radius: 10px;margin-bottom: 5px;" src="" onerror="this.onerror=null;this.src='/static/img/1280x720_Placeholder.png';"></a>
                    <a href=""><h4 class="card-title" style="margin-top: 5px;">Video Title</h4></a>
                    <a href=""><h6 class="text-muted card-subtitle mb-2">Channel Name</h6></a>
                </div>
            </div>
        </div>
    </div>
    <script>
        var url = "http://127.0.0.1:8000/video/dash/{id}/{id}.mpd"; // Path to your DASH manifest file
        var video = document.querySelector("#videoPlayer");
        var player = dashjs.MediaPlayer().create();
        player.initialize(video, url, true);
        console.log(player.getBitrateInfoListFor("video"));
        
        var xhr = new XMLHttpRequest();
        xhr.open('GET', 'http://127.0.0.1:8000/video/videos/{id}', true);
        xhr.onload = function() {{
          if(xhr.status === 200) {{
            var data = JSON.parse(xhr.responseText);
            console.log(data);
            document.querySelector("#videoTitle").innerText = data.title;
            document.querySelector("#videoDescription").innerText = data.description;
            document.querySelector("#channelName").innerText = `${{data.name}} (@${{data.username}})`;
            document.querySelector("#channelName").parentElement.href = `/channel/${{data.author_id}}`;
          }} else {{
            console.error('Error:', xhr.statusText);
          }}
        }};
        xhr.send();
    </script>
    <script>
        let lastTimestamp = null;
        let loading = false;
        
        window.jdenticon_config = {{
            lightness: {{
                color: [0.35, 1.00],
                grayscale: [0.33, 1.00]
            }},
            saturation: {{
                color: 1.00,
                grayscale: 1.00
            }},
            backColor: "#000"
        }};

        function timeAgo(dateString) {{
            const seconds = Math.floor((new Date() - new Date(dateString)) / 1000);
            const intervals = [
                {{ label: 'year', seconds: 31536000 }},
                {{ label: 'month', seconds: 2592000 }},
                {{ label: 'day', seconds: 86400 }},
                {{ label: 'hour', seconds: 3600 }},
                {{ label: 'minute', seconds: 60 }},
                {{ label: 'second', seconds: 1 }},
            ];
    
            for (const {{ label, seconds: intervalSeconds }} of intervals) {{
                const count = Math.floor(seconds / intervalSeconds);
                if (count) return `${{count}} ${{label}}${{count > 1 ? 's' : ''}} ago`;
            }}
            return 'just now';
        }}
        
        function loadComments() {{
            if (loading) return;
            loading = true;

            let xhr = new XMLHttpRequest();
            let url = `http://127.0.0.1:8000/engagement/comments?video_id={id}`;

            if (lastTimestamp) {{
                url += `&last_timestamp=${{encodeURIComponent(lastTimestamp)}}`;
            }}

            xhr.open('GET', url, true);
            xhr.onreadystatechange = function () {{
                if (xhr.readyState == 4 && xhr.status == 200) {{
                    let response = JSON.parse(xhr.responseText);
                    console.log(response);
                    const commentsSection = document.getElementById('commentsSection');
                    const commentTemplate = document.getElementById("commentTemplate");

                    response.comments.forEach(function (comment) {{
                        const commentElement = commentTemplate.cloneNode(true);
                        commentElement.id = comment.id;
                        commentElement.querySelector("#content").innerText = comment.comment_text;
                        commentElement.querySelector("#timestamp").innerText = timeAgo(comment.timestamp+"Z");
                        
                        commentElement.querySelector("#author").innerText = comment.username;
                        jdenticon.update(commentElement.querySelector("#authorIcon"), comment.username);
                        
                        
                        commentElement.style = "margin-left:20px";

                        commentsSection.appendChild(commentElement);
                    }});

                    lastTimestamp = response.last_timestamp;
                    document.getElementById('amountComments').innerText = response.commentCount;
                    document.getElementById('commentSpinner').style = "display:none;";

                    if (!response.has_more) {{
                        document.getElementById('load-more').style = "display:none;";
                    }} else {{
                        document.getElementById('load-more').style = "";
                    }}

                    loading = false;
                }}
            }};

            xhr.send();
        }}

        window.onload = loadComments;
    </script>
    <script src="/static/js/recommendVideos.js"></script>
    <script>getRecommendations('{id}');</script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>

</html>
'''