from types import SimpleNamespace
from unittest.mock import patch
import pytest
from werkzeug.exceptions import Unauthorized
from seedboxsync.front import login_manager as login_manager_module


def test_load_user_delegates_to_user_model():
    user = object()
    with patch.object(login_manager_module.User, "get", return_value=user) as get_user:
        assert login_manager_module.load_user("42") is user
    get_user.assert_called_once_with("42")


def test_request_loader_rejects_missing_or_incomplete_basic_auth():
    assert login_manager_module.load_user_from_request(SimpleNamespace(authorization=None)) is None
    assert login_manager_module.load_user_from_request(SimpleNamespace(authorization=SimpleNamespace(type="bearer"))) is None
    auth = SimpleNamespace(type="basic", username=None, password="secret")
    assert login_manager_module.load_user_from_request(SimpleNamespace(authorization=auth)) is None


def test_request_loader_authenticates_basic_credentials():
    user = object()
    auth = SimpleNamespace(type="basic", username="alice", password="secret")
    with patch.object(login_manager_module.User, "authenticate", return_value=user) as authenticate:
        assert login_manager_module.load_user_from_request(SimpleNamespace(authorization=auth)) is user
    authenticate.assert_called_once_with("alice", "secret")


def test_request_loader_handles_unknown_user():
    auth = SimpleNamespace(type="basic", username="alice", password="secret")
    with patch.object(login_manager_module.User, "authenticate", side_effect=login_manager_module.User.DoesNotExist):
        assert login_manager_module.load_user_from_request(SimpleNamespace(authorization=auth)) is None


def test_unauthorized_api_request_aborts_with_401():
    with patch.object(login_manager_module, "request", SimpleNamespace(blueprint="api")), pytest.raises(Unauthorized):
        login_manager_module.unauthorized()


def test_unauthorized_frontend_request_redirects_to_login(app):
    with app.test_request_context("/private"):
        response = login_manager_module.unauthorized()

    assert response.status_code == 302
    assert "/login?next=" in response.location
