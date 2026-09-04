import re
from unittest.mock import patch
from seedboxsync.core.dao import User


def _csrf_token(client, path):
    response = client.get(path)
    match = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', response.text)
    assert match is not None, (response.status_code, response.location, response.text[:200])
    return match.group(1)


def _login(client, login, password, next_url="", csrf_token=None):
    path = "/login"
    if next_url:
        path += f"?next={next_url}"
    return client.post(
        path,
        data={
            "csrf_token": csrf_token or _csrf_token(client, "/login"),
            "login": login,
            "password": password,
        },
    )


def test_login_rejects_invalid_credentials(client):
    response = _login(client, "unknown", "unknownunknownunknownunknown")

    assert response.status_code == 200
    assert b"`Invalid username or password.`" in response.data


def test_login_redirects_authenticated_user_to_homepage(client):
    csrf_token = _csrf_token(client, "/login")
    user = User(id=1, username="alice", email="alice@example.com")

    with patch("seedboxsync.front.views.auth.login.User.authenticate", return_value=user):
        response = _login(client, "alice", "secretsecret", csrf_token=csrf_token)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_login_preserves_next_url(client):
    csrf_token = _csrf_token(client, "/login")
    user = User(id=1, username="alice", email="alice@example.com")

    with patch("seedboxsync.front.views.auth.login.User.authenticate", return_value=user):
        response = _login(client, "alice@example.com", "secretsecret", "/settings", csrf_token)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/settings")
