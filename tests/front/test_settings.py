import re
from unittest.mock import patch
import pytest
from seedboxsync.core.dao import SeedboxSync


def _post_form(client, path, form):
    csrf_response = client.get(path)
    csrf_token = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', csrf_response.text).group(1)
    return client.post(path, data={**form, "csrf_token": csrf_token})


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
            "/settings",
            {
                "sync_blackhole_enabled": "1",
                "webui_theme": "dark",
                "webui_language": "fr",
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
    with patch("seedboxsync.front.views.settings._save_form") as save_form:
        response = _post_form(client, "/settings/seedbox", {"seedbox_host": ""})

    assert response.status_code == 200
    save_form.assert_not_called()


@pytest.mark.parametrize(
    ("path", "form"),
    [
        ("/settings", {"sync_blackhole_enabled": "1", "webui_theme": "dark", "webui_language": "auto"}),
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
        ),
        ("/settings/nas", {"local_watch_path": "/watch", "local_download_path": "/downloads"}),
        ("/settings/ping", {"healthchecks_sync_blackhole_ping_url": "https://hc-ping.com/test"}),
    ],
)
def test_settings_views_report_persistence_errors(client, path, form):
    with patch("seedboxsync.front.views.settings._save_form", side_effect=RuntimeError("database unavailable")):
        response = _post_form(client, path, form)

    assert response.status_code == 200
    assert b"Failed to save config" in response.data
