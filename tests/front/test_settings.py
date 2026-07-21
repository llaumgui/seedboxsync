from unittest.mock import patch
from seedboxsync.core.dao import SeedboxSync
from seedboxsync.front.views.settings import _as_bool


def _valid_settings_form(app):
    form = {}
    for key, value in app.seedboxsync_config.items():
        if key.endswith("_enabled"):
            form[key] = "1" if value else "0"
        else:
            form[key] = "" if value is False else str(value)

    form.update(
        seedbox_host="storage.example",
        seedbox_port="2222",
        seedbox_login="alice",
        seedbox_password="secret",
        seedbox_protocol="sftp",
        seedbox_tmp_path="/remote/tmp",
        seedbox_watch_path="/remote/watch",
        seedbox_finished_path="/remote/files",
        seedbox_part_suffix=".partial",
    )
    return form


def test_settings_rejects_missing_required_fields(client):
    response = client.post("/settings", data={"seedbox_host": "storage.example"})

    assert response.status_code == 200
    assert b"Missing required fields" in response.data


def test_settings_persists_cleaned_form_values(app, client):
    form = _valid_settings_form(app)
    form["seedbox_host"] = "  storage.example  "
    form["seedbox_timeout_enabled"] = "0"
    form["seedbox_chmod_enabled"] = "0"

    response = client.post("/settings", data=form)

    assert response.status_code == 200
    assert app.config["SEEDBOXSYNC_SEEDBOX_HOST"] == "storage.example"
    assert app.config["SEEDBOXSYNC_SEEDBOX_TIMEOUT"] is False
    assert app.config["SEEDBOXSYNC_SEEDBOX_CHMOD"] is False
    with app.app_context():
        stored = {
            row.key: row.value
            for row in SeedboxSync.select().where(
                SeedboxSync.key.in_([
                    "config_seedbox_host",
                    "config_seedbox_timeout",
                    "config_seedbox_chmod",
                ])
            )
        }
    assert stored == {
        "config_seedbox_host": "storage.example",
        "config_seedbox_timeout": "0",
        "config_seedbox_chmod": "0",
    }


def test_settings_reports_persistence_errors(app, client):
    with patch("seedboxsync.front.views.settings._save_form", side_effect=RuntimeError("database unavailable")):
        response = client.post("/settings", data=_valid_settings_form(app))

    assert response.status_code == 200
    assert b"Failed to save configuration" in response.data


def test_settings_boolean_parser_accepts_only_enabled_form_value():
    assert _as_bool(" 1 ") is True
    assert _as_bool("true") is False
    assert _as_bool(None) is False
