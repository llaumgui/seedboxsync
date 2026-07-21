from unittest.mock import patch
from seedboxsync.core.ping.client.healthchecks import Healthchecks

PING_URL = "https://healthchecks.dev/ping/12345678-1234-1234-1234-123456789012"


def test_healthchecks_sends_start_and_success_pings(app, mock_urllib):
    app.config.update(
        SEEDBOXSYNC_HEALTHCHECKS_SYNC_SEEDBOX_ENABLED=True,
        SEEDBOXSYNC_HEALTHCHECKS_SYNC_SEEDBOX_PING_URL=PING_URL,
    )

    with app.app_context():
        healthchecks = Healthchecks()
        healthchecks.start("sync_seedbox")
        healthchecks.success("sync_seedbox")

    assert mock_urllib.call_count == 2
    assert mock_urllib.call_args_list[0].args == (f"{PING_URL}/start",)
    assert mock_urllib.call_args_list[0].kwargs == {"timeout": 10}
    assert mock_urllib.call_args_list[1].args == (PING_URL,)
    assert mock_urllib.call_args_list[1].kwargs == {"timeout": 10}


def test_disabled_healthchecks_does_not_issue_requests(app, mock_urllib, caplog):
    app.config["SEEDBOXSYNC_HEALTHCHECKS_SYNC_BLACKHOLE_ENABLED"] = False
    caplog.set_level("INFO", logger=app.logger.name)

    with app.app_context():
        healthchecks = Healthchecks()
        healthchecks.start("sync_blackhole")
        healthchecks.success("sync_blackhole")

    mock_urllib.assert_not_called()
    assert 'Healthchecks for "sync_blackhole" disabled' in caplog.text


def test_healthchecks_logs_start_and_success_ping_failures(app, mock_urllib):
    app.config.update(
        SEEDBOXSYNC_HEALTHCHECKS_SYNC_SEEDBOX_ENABLED=True,
        SEEDBOXSYNC_HEALTHCHECKS_SYNC_SEEDBOX_PING_URL=PING_URL,
    )
    mock_urllib.side_effect = OSError("network unavailable")

    with app.app_context(), patch.object(app.logger, "exception") as log:
        healthchecks = Healthchecks()
        healthchecks.start("sync_seedbox")
        healthchecks.success("sync_seedbox")

    assert log.call_args_list[0].args == ("Healthchecks, ping failed",)
    assert log.call_args_list[1].args == ("Healthchecks, ping failed.",)
