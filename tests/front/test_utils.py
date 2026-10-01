from unittest.mock import patch
from seedboxsync.core import Config
from seedboxsync.core.database.models import SeedboxSync
from seedboxsync.front.utils import is_safe_redirect_url, save_settings_form, toast


def test_is_safe_redirect_url_accepts_only_local_absolute_paths():
    assert is_safe_redirect_url("/settings")
    assert is_safe_redirect_url("/settings?tab=api")
    assert not is_safe_redirect_url("settings")
    assert not is_safe_redirect_url("https://example.org")
    assert not is_safe_redirect_url("//example.org")
    assert not is_safe_redirect_url("/\\example.org")
    with patch("seedboxsync.front.utils.urlsplit", side_effect=ValueError):
        assert not is_safe_redirect_url("/malformed")


def test_toast_stores_message_and_emits_flask_signal(app):
    with app.test_request_context("/"):
        with patch("seedboxsync.front.utils.message_flashed.send") as send:
            toast("Saved", "Settings", "success")

        from flask import session

        assert session["_toasts"] == [("success", "Saved", "Settings")]
        send.assert_called_once()
        assert send.call_args.kwargs["message"] == "Saved"
        assert send.call_args.kwargs["category"] == "success"


class _Field:
    def __init__(self, name, data):
        self.name = name
        self.data = data


class _Form:
    def __init__(self, fields):
        self.fields = {field.name: field for field in fields}

    def __iter__(self):
        return iter(self.fields.values())

    def __contains__(self, name):
        return name in self.fields

    def __getitem__(self, name):
        return self.fields[name]


def test_save_settings_form_overrides_disabled_options_and_skips_control_fields(app):
    form = _Form(
        [
            _Field("seedbox_timeout", "30"),
            _Field("seedbox_chmod", "0o644"),
            _Field("login_disabled", "1"),
            _Field("csrf_token", "ignored"),
            _Field("submit", "ignored"),
        ]
    )

    with app.test_request_context("/settings", method="POST", data={}):
        save_settings_form(form)

    assert app.config[f"{Config.CONFIG_NAMESPACE}SEEDBOX_TIMEOUT"] is False
    assert app.config[f"{Config.CONFIG_NAMESPACE}SEEDBOX_CHMOD"] is False
    assert app.config["LOGIN_DISABLED"] is True
    assert form["seedbox_timeout"].data == "0"
    assert form["seedbox_chmod"].data == "0"

    with app.app_context():
        stored = {row.key: row.value for row in SeedboxSync.select().where(SeedboxSync.key.in_(["config_seedbox_timeout", "config_seedbox_chmod"]))}

    assert stored == {"config_seedbox_timeout": "0", "config_seedbox_chmod": "0"}
