import re
from unittest.mock import patch
from seedboxsync.core.dao import User


def _csrf_token(client, path):
    response = client.get(path)
    match = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', response.text)
    assert match is not None, (response.status_code, response.location, response.text[:200])
    return match.group(1)


def _login_as_first_user(app, client):
    with app.app_context():
        user_id = User.select(User.id).first().id
    with client.session_transaction() as session:
        session["_user_id"] = str(user_id)
        session["_fresh"] = True
    return user_id


def test_settings_users_lists_users(app, client):
    _login_as_first_user(app, client)

    response = client.get("/settings/users")

    assert response.status_code == 200
    assert b"Users" in response.data


def test_settings_users_create_persists_user(app, client):
    _login_as_first_user(app, client)
    path = "/settings/users/create"
    form = {
        "username": "created-user",
        "email": "created@example.com",
        "password": "secretsecret",
        "password2": "secretsecret",
        "csrf_token": _csrf_token(client, path),
    }

    response = client.post(path, data=form)

    assert response.status_code == 302
    with app.app_context():
        user = User.get(User.username == "created-user")
    assert user.email == "created@example.com"


def test_settings_users_edit_updates_user(app, client):
    user_id = _login_as_first_user(app, client)
    path = f"/settings/users/{user_id}/edit"

    response = client.post(
        path,
        data={
            "username": "edited-user",
            "email": "edited@example.com",
            "password": "new-secret",
            "password2": "new-secret",
            "csrf_token": _csrf_token(client, "/settings/users/create"),
        },
    )

    assert response.status_code == 302
    with app.app_context():
        user = User.get_by_id(user_id)
        assert user.username == "edited-user"
        assert user.email == "edited@example.com"


def test_settings_users_edit_rejects_password_mismatch(app, client):
    user_id = _login_as_first_user(app, client)
    path = f"/settings/users/{user_id}/edit"
    csrf_token = _csrf_token(client, "/settings/users/create")

    with patch("seedboxsync.front.views.users.render_template", return_value="form rendered"):
        response = client.post(
            path,
            data={
                "username": "unchanged-user",
                "email": "unchanged@example.com",
                "password": "new-secret",
                "password2": "other-secret",
                "csrf_token": csrf_token,
            },
        )

    assert response.status_code == 200


def test_settings_users_edit_returns_404_for_unknown_user(app, client):
    _login_as_first_user(app, client)
    response = client.get("/settings/users/999999/edit")
    assert response.status_code == 404


def test_settings_users_create_rejects_password_mismatch(app, client):
    _login_as_first_user(app, client)
    path = "/settings/users/create"

    response = client.post(
        path,
        data={
            "username": "not-created",
            "email": "missing@example.com",
            "password": "new-secret",
            "password2": "other-secret",
            "csrf_token": _csrf_token(client, path),
        },
    )

    assert response.status_code == 200
    assert b"Passwords do not match" in response.data
    with app.app_context():
        assert User.select().where(User.username == "not-created").count() == 0


def test_settings_users_delete_removes_user(app, client):
    with app.app_context():
        user = User.create(username="delete-me", email="delete@example.com", password="hashed")
        user_id = user.id
    _login_as_first_user(app, client)
    path = f"/settings/users/{user_id}/delete"

    response = client.post(path, data={"csrf_token": _csrf_token(client, "/settings/users/create")})

    assert response.status_code == 302
    with app.app_context():
        assert User.select().where(User.id == user_id).count() == 0


def test_settings_users_delete_returns_404_for_unknown_user(app, client):
    _login_as_first_user(app, client)
    response = client.get("/settings/users/999999/delete")
    assert response.status_code == 404
