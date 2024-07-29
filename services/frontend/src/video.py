from __main__ import app

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
    <form action="http://localhost:8000/video/videos" method="POST" enctype="multipart/form-data">
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
    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DASH Player</title>
    <script src="https://cdn.dashjs.org/latest/dash.all.min.js"></script>
</head>
<body>
    <h1>DASH Player</h1>
    <video id="videoPlayer" data-dashjs-player width="1080" height="720" loop="true" autoplay="true" controls crossorigin="anonymous">
        <track
    label="English"
    kind="subtitles"
    srclang="en"
    src="http://localhost:5002/dash/{id}/{id}.vtt"
    default />
    </video>
    <script>
        var url = "http://localhost:5002/dash/{id}/{id}.mpd"; // Path to your DASH manifest file
        var video = document.querySelector("#videoPlayer");
        var player = dashjs.MediaPlayer().create();
        player.initialize(video, url, true);
        console.log(player.getBitrateInfoListFor("video"));
    </script>
</body>
</html>
'''