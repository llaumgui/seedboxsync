from unittest.mock import patch
import pytest
from seedboxsync.core.config import Config
from seedboxsync.core.dao import SeedboxSync


@pytest.mark.parametrize(
    ("key", "raw_value", "expected"),
    [
        ("SEEDBOXSYNC_SYNC_SEEDBOX_ENABLED", "1", True),
        ("SEEDBOXSYNC_SYNC_SEEDBOX_ENABLED", "0", False),
        ("SEEDBOXSYNC_SYNC_SEEDBOX_ENABLED", "", False),
        ("SEEDBOXSYNC_SEEDBOX_TIMEOUT", "30", 30),
        ("SEEDBOXSYNC_SEEDBOX_TIMEOUT", "0", False),
        ("SEEDBOXSYNC_SEEDBOX_TIMEOUT", None, False),
        ("SEEDBOXSYNC_SEEDBOX_CHMOD", "0640", "0640"),
        ("SEEDBOXSYNC_SEEDBOX_CHMOD", "0", False),
        ("SEEDBOXSYNC_SEEDBOX_HOST", "seedbox.example", "seedbox.example"),
    ],
)
def test_database_configuration_values_are_converted_by_option_type(key, raw_value, expected):
    assert Config._convert_config_value(key, raw_value) == expected


def test_reload_config_merges_known_database_values_and_ignores_unknown_ones(app):
    with app.app_context():
        SeedboxSync.replace(key="config_seedbox_host", value="storage.example").execute()
        SeedboxSync.replace(key="config_seedbox_timeout", value="45").execute()
        SeedboxSync.replace(key="config_unknown", value="ignored").execute()

        with patch.object(app.logger, "warning") as warning:
            config = Config.reload_config(app)

    assert config["SEEDBOXSYNC_SEEDBOX_HOST"] == "storage.example"
    assert config["SEEDBOXSYNC_SEEDBOX_TIMEOUT"] == 45
    assert "SEEDBOXSYNC_UNKNOWN" not in config
    warning.assert_called_once_with("Ignoring unknown configuration key: %s", "config_unknown")


def test_password_is_masked_when_database_configuration_is_logged(app):
    with app.app_context():
        SeedboxSync.replace(key="config_seedbox_password", value="super-secret").execute()

        with patch.object(app.logger, "debug") as debug:
            Config.reload_config(app)

    logged_values = [str(call) for call in debug.call_args_list]
    assert any("*****" in value for value in logged_values)
    assert all("super-secret" not in value for value in logged_values)
