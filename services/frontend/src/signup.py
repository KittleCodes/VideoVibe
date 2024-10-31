from __main__ import app

@app.route('/signup')
def signup():
    return '''
<!DOCTYPE html>
<html data-bs-theme="light" lang="en">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
    <title>VideoVibe</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootswatch@5.3.3/dist/darkly/bootstrap.min.css">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,400;0,700;1,400&amp;display=swap">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Almarai&amp;display=swap">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/ionicons/2.0.1/css/ionicons.min.css">
</head>

<body>
    <section class="position-relative py-4 py-xl-5">
        <div class="container">
            <div class="row mb-5">
                <div class="col-md-8 col-xl-6 text-center mx-auto">
                    <h2>Sign up</h2>
                    <p class="w-lg-50">Signup to access more features such as subscribing to channels, creating playlists, and uploading your own content.</p>
                </div>
            </div>
            <div class="row d-flex justify-content-center">
                <div class="col-md-6 col-xl-4">
                    <div class="card mb-5">
                        <div class="card-body d-flex flex-column align-items-center">
                            <div class="bs-icon-xl bs-icon-circle bs-icon-primary bs-icon my-4"><i class="icon ion-ios-paper-outline"></i></div>
                            <form class="text-center">
                                <div class="mb-3"><input class="form-control" type="email" id="email" placeholder="Email"></div>
                                <div class="mb-3"><input class="form-control" type="password" id="password" placeholder="Password"></div>
                                <div class="mb-3"><button class="btn btn-primary d-block w-100" type="button" onclick="signup()">Signup</button></div>
                                <p class="text-muted">Already have an account? Click&nbsp;<a href="/login">here</a>&nbsp;</p>
                            </form>
                        </div>
                    </div><a class="text-center d-xl-flex justify-content-xl-center" href="/">Return home</a>
                </div>
            </div>
        </div>
    </section>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/js/auth.js"></script>
</body>

</html>
'''
