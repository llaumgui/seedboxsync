from pathlib import Path
import re
from unittest.mock import patch
import pytest
from werkzeug.security import generate_password_hash
from seedboxsync.core.database.models import ApiKey, SeedboxSync, User
from seedboxsync.front.forms import SettingsAuthenticationForm
from seedboxsync.front.utils import save_settings_form
from seedboxsync.front.views.auth.logout import logout
from seedboxsync.front.views.settings.apikeys import apikeys, apikeys_create, apikeys_delete
from seedboxsync.front.views.settings.authentication import authentication


@pytest.fixture(autouse=True)
def _ensure_repo_root(monkeypatch):
    monkeypatch.chdir(Path(__file__).resolve().parents[4])


def _post_form(client, path, form):
    csrf_response = client.get(path)
    data = dict(form)

    csrf_match = re.search(r'name="csrf_token"\s+type="hidden"\s+value="([^"]+)"', csrf_response.text)
    if csrf_match is not None:
        data["csrf_token"] = csrf_match.group(1)

    return client.post(path, data=data)


@pytest.mark.parametrize(
    ("path", "title"),
    [
        ("/settings", b"SeedboxSync"),
        ("/settings/seedbox", b"Seedbox"),
        ("/settings/nas", b"Local (NAS)"),
        ("/settings/ping", b"Healthchecks"),
    ],
)
def test_settings_views_are_reachable(client, path, title):
    response = client.get(path)

    assert response.status_code == 200
    assert title in response.data


@pytest.mark.parametrize(
    ("path", "form", "config", "stored"),
    [
        (
            "/settings/seedboxsync",
            {
                "sync_blackhole_enabled": "1",
                "webui_theme": "dark",
                "webui_language": "fr_FR",
            },
            {"SEEDBOXSYNC_SYNC_BLACKHOLE_ENABLED": True, "SEEDBOXSYNC_SYNC_SEEDBOX_ENABLED": False},
            {"config_sync_blackhole_enabled": "1", "config_sync_seedbox_enabled": "0"},
        ),
        (
            "/settings/seedbox",
            {
                "seedbox_host": "storage.example",
                "seedbox_port": "2222",
                "seedbox_login": "alice",
                "seedbox_password": "secret",
                "seedbox_timeout": "30",
                "seedbox_timeout_enabled": "1",
                "seedbox_protocol": "sftp",
                "seedbox_chmod": "0o644",
                "seedbox_chmod_enabled": "1",
                "seedbox_max_concurrent_prefetch_requests": "128",
                "seedbox_tmp_path": "/remote/tmp",
                "seedbox_watch_path": "/remote/watch",
                "seedbox_finished_path": "/remote/files",
                "seedbox_prefixed_path": "/files",
                "seedbox_part_suffix": ".partial",
                "seedbox_exclude_syncing": "",
            },
            {"SEEDBOXSYNC_SEEDBOX_HOST": "storage.example"},
            {"config_seedbox_host": "storage.example"},
        ),
        (
            "/settings/nas",
            {"local_watch_path": "/local/watch", "local_download_path": "/local/downloads"},
            {"SEEDBOXSYNC_LOCAL_WATCH_PATH": "/local/watch"},
            {"config_local_watch_path": "/local/watch"},
        ),
        (
            "/settings/ping",
            {
                "healthchecks_sync_blackhole_enabled": "1",
                "healthchecks_sync_blackhole_ping_url": "https://hc-ping.com/blackhole",
                "healthchecks_sync_seedbox_ping_url": "",
            },
            {"SEEDBOXSYNC_HEALTHCHECKS_SYNC_BLACKHOLE_ENABLED": True},
            {"config_healthchecks_sync_blackhole_enabled": "1"},
        ),
    ],
)
def test_settings_views_persist_valid_form_values(app, client, path, form, config, stored):
    response = _post_form(client, path, form)

    assert response.status_code == 200
    for key, value in config.items():
        assert app.config[key] == value

    with app.app_context():
        persisted = {row.key: row.value for row in SeedboxSync.select().where(SeedboxSync.key.in_(list(stored)))}
    assert persisted == stored


def test_seedbox_settings_rejects_missing_required_fields(client):
    with patch("seedboxsync.front.utils.save_settings_form") as save_form:
        response = _post_form(client, "/settings/seedbox", {"seedbox_host": ""})

    assert response.status_code == 200
    save_form.assert_not_called()


def test_save_settings_form_persists_runtime_and_database_values(app):
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_request_context("/settings", method="POST", data={"login_disabled": "1", "auth_gravatar_enabled": "1"}):
        form = SettingsAuthenticationForm(meta={"csrf": False}, data={"login_disabled": True, "auth_gravatar_enabled": True})
        save_settings_form(form)

    assert app.config["LOGIN_DISABLED"] is True
    assert app.config["SEEDBOXSYNC_LOGIN_DISABLED"] is True
    assert app.config["SEEDBOXSYNC_AUTH_GRAVATAR_ENABLED"] is True

    with app.app_context():
        persisted = {row.key: row.value for row in SeedboxSync.select().where(SeedboxSync.key.in_(["config_login_disabled", "config_auth_gravatar_enabled"]))}

    assert persisted["config_login_disabled"] == "1"
    assert persisted["config_auth_gravatar_enabled"] == "1"


def test_authentication_settings_page_saves_oauth_configuration(app):
    app.config["WTF_CSRF_ENABLED"] = False
    with (
        patch("seedboxsync.front.views.settings.authentication.save_settings_form") as save_form,
        patch("seedboxsync.front.views.settings.authentication.init_oauth2") as init_oauth2_mock,
        app.test_request_context(
            "/settings/authentication",
            method="POST",
            data={"login_disabled": "1", "oauth_enabled": "1", "oauth_name": "oidc"},
        ),
    ):
        response = authentication()

    save_form.assert_called_once()
    init_oauth2_mock.assert_called_once()
    assert response
    assert "Configuration saved successfully" in response


def test_apikeys_list_and_create_delete_flow(app):
    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        user = User.create(username="alice", password=generate_password_hash("secret"), email="alice@example.com")

    with app.test_request_context("/settings/apikeys"):
        with patch("seedboxsync.front.views.settings.apikeys.current_user", user):
            response = apikeys()
        assert isinstance(response, str)

    with (
        app.test_request_context("/settings/apikeys/create", method="POST", data={"name": "homeassistant"}),
        patch("seedboxsync.front.views.settings.apikeys.current_user", user),
    ):
        response = apikeys_create()

    assert response.status_code == 302
    assert response.location.endswith("/settings/apikeys")

    with app.app_context():
        apikey = ApiKey.get(user=user)
        assert apikey.name == "homeassistant"

    with app.test_request_context(f"/settings/apikeys/{apikey.id}/delete", method="POST"), patch("seedboxsync.front.views.settings.apikeys.current_user", user):
        response = apikeys_delete(apikey.id)

    assert response.status_code == 302
    assert response.location.endswith("/settings/apikeys")

    with app.app_context():
        assert ApiKey.get_or_none(ApiKey.id == apikey.id) is None


def test_api_key_generation_and_authentication(app):
    with app.app_context():
        user = User.create(username="bob", password=generate_password_hash("secret"), email="bob@example.com")
        api_key, raw_key = ApiKey.generate(user, "cli")

        assert raw_key.startswith("sbx_")
        assert api_key.key_hash != raw_key
        assert ApiKey.authenticate(raw_key) == user
        assert ApiKey.authenticate("sbx_invalid") is None
        assert ApiKey.authenticate("other_123") is None

        refreshed = ApiKey.get_by_id(api_key.id)
        assert refreshed is not None
        assert refreshed.last_used is not None


def test_logout_view_redirects_to_frontpage(app):
    with app.test_request_context("/logout"), patch("seedboxsync.front.views.auth.logout.logout_user") as logout_user_mock:
        response = logout()

    assert response.status_code == 302
    assert response.location.endswith("/")
    logout_user_mock.assert_called_once()


@pytest.mark.parametrize(
    ("path", "form", "save_settings_target"),
    [
        (
            "/settings/seedboxsync",
            {"sync_blackhole_enabled": "1", "webui_theme": "dark", "webui_language": "auto"},
            "seedboxsync.front.views.settings.seedboxsync.save_settings_form",
        ),
        (
            "/settings/seedbox",
            {
                "seedbox_host": "storage.example",
                "seedbox_port": "2222",
                "seedbox_login": "alice",
                "seedbox_password": "secret",
                "seedbox_max_concurrent_prefetch_requests": "128",
                "seedbox_tmp_path": "/tmp",
                "seedbox_watch_path": "/watch",
                "seedbox_finished_path": "/files",
            },
            "seedboxsync.front.views.settings.seedbox.save_settings_form",
        ),
        (
            "/settings/nas",
            {"local_watch_path": "/watch", "local_download_path": "/downloads"},
            "seedboxsync.front.views.settings.nas.save_settings_form",
        ),
        (
            "/settings/ping",
            {"healthchecks_sync_blackhole_ping_url": "https://hc-ping.com/test"},
            "seedboxsync.front.views.settings.ping.save_settings_form",
        ),
    ],
)
def test_settings_views_report_persistence_errors(client, path, form, save_settings_target):
    with patch(save_settings_target, side_effect=RuntimeError("database unavailable")):
        response = _post_form(client, path, form)

    assert response.status_code == 200
    assert b"Failed to save config" in response.data


def test_infos(client):  # Is OK
    response = client.get("/settings/info")
    assert response.status_code == 200
