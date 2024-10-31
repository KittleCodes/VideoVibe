var $ = function(id)
{
    return document.getElementById(id);
}

function login()
{
    let email = $("email");
    let password = $("password");

    let xhr = new XMLHttpRequest();
    let url = "http://127.0.0.1:8000/auth/login";

    xhr.open("POST", url, true);

    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            let json = JSON.parse(xhr.responseText);
            console.log(json);
            document.cookie = "access_token=" + json.access_token;
        }
    };

    var data = JSON.stringify({ "email": email.value, "password": password.value });

    xhr.send(data);
}

function signup()
{
    let email = $("email");
    let password = $("password");

    let xhr = new XMLHttpRequest();
    let url = "http://127.0.0.1:8000/user/register";

    xhr.open("POST", url, true);

    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            let json = JSON.parse(xhr.responseText);
            console.log(json);
        }
    };

    var data = JSON.stringify({ "email": email.value, "password": password.value });

    xhr.send(data);
}