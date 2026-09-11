from datetime import datetime
from unittest.mock import MagicMock, patch
from seedboxsync.core.database.models import User


def test_authorize_redirects_to_login_when_provider_is_not_configured(client):
    with patch("seedboxsync.front.views.auth.authorize.oauth.create_client", return_value=None):
        response = client.get("/oauth2/oidc/callback")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_authorize_redirects_to_login_when_provider_does_not_return_email(client):
    provider = MagicMock()
    provider.authorize_access_token.return_value = {"access_token": "token"}
    provider.userinfo.return_value = {"preferred_username": "alice"}

    with patch("seedboxsync.front.views.auth.authorize.oauth.create_client", return_value=provider):
        response = client.get("/oauth2/oidc/callback")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
    provider.userinfo.assert_called_once_with(token={"access_token": "token"})


def test_authorize_creates_and_logs_in_oidc_user(app, client):
    user = User(id=42, username="alice", email="alice@example.com")
    provider = MagicMock()
    provider.authorize_access_token.return_value = {"access_token": "token"}
    provider.userinfo.return_value = {"email": "alice@example.com", "name": "Alice"}
    app.config["SEEDBOXSYNC_OAUTH_AUTO_CREATE_USER_ENABLED"] = True

    with (
        patch("seedboxsync.front.views.auth.authorize.oauth.create_client", return_value=provider),
        patch("seedboxsync.front.views.auth.authorize.secrets.token_urlsafe", return_value="random-password"),
        patch("seedboxsync.front.views.auth.authorize.generate_password_hash", return_value="hashed-password"),
        patch("seedboxsync.front.views.auth.authorize.User.get_or_create", return_value=(user, True)) as get_or_create,
        patch("seedboxsync.front.views.auth.authorize.login_user") as login_user,
    ):
        response = client.get("/oauth2/oidc/callback")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")
    get_or_create.assert_called_once_with(
        email="alice@example.com",
        defaults={"username": "Alice", "origin": User.ORIGIN_OIDC, "password": "hashed-password"},
    )
    login_user.assert_called_once_with(user)
    assert isinstance(user.last_login, datetime)


def test_authorize_logs_in_existing_user_without_creating(app, client):
    user = MagicMock(email="alice@example.com")
    provider = MagicMock()
    provider.authorize_access_token.return_value = {"access_token": "token"}
    provider.userinfo.return_value = {"email": "alice@example.com", "preferred_username": "alice"}

    app.config["SEEDBOXSYNC_OAUTH_AUTO_CREATE_USER_ENABLED"] = False
    with (
        patch("seedboxsync.front.views.auth.authorize.oauth.create_client", return_value=provider),
        patch("seedboxsync.front.views.auth.authorize.User.get", return_value=user) as get_user,
        patch("seedboxsync.front.views.auth.authorize.login_user") as login_user,
    ):
        response = client.get("/oauth2/oidc/callback")

    assert response.status_code == 302
    get_user.assert_called_once_with(User.email == "alice@example.com")
    login_user.assert_called_once_with(user)


def test_authorize_redirects_to_login_when_authentication_fails(client):
    with patch("seedboxsync.front.views.auth.authorize.oauth.create_client", side_effect=RuntimeError("boom")):
        response = client.get("/oauth2/oidc/callback")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_authorize_redirects_to_login_when_access_token_exchange_fails(client):
    provider = MagicMock()
    provider.authorize_access_token.side_effect = RuntimeError("boom")

    with patch("seedboxsync.front.views.auth.authorize.oauth.create_client", return_value=provider):
        response = client.get("/oauth2/oidc/callback")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
