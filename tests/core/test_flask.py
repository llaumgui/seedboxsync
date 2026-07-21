from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest


def test_sync_client_is_loaded_from_configured_protocol_and_cached(app):
    transfer_client = MagicMock(return_value=object())
    module = SimpleNamespace(SftpClient=transfer_client)
    app.config["SEEDBOXSYNC_SEEDBOX_PROTOCOL"] = "sftp"

    with patch("seedboxsync.core.flask.import_module", return_value=module) as import_module:
        first = app.sync
        second = app.sync

    assert first is second
    import_module.assert_called_once_with("seedboxsync.core.sync.client.sftp")
    transfer_client.assert_called_once_with()


def test_sync_reports_an_unsupported_protocol(app):
    app.config["SEEDBOXSYNC_SEEDBOX_PROTOCOL"] = "unknown"

    with patch("seedboxsync.core.flask.import_module", side_effect=ImportError("missing module")), pytest.raises(SystemExit) as error:
        _ = app.sync

    assert "Unsupported protocol: unknown" in str(error.value)


def test_sync_reports_a_protocol_module_without_expected_client(app):
    app.config["SEEDBOXSYNC_SEEDBOX_PROTOCOL"] = "ftp"

    with patch("seedboxsync.core.flask.import_module", return_value=SimpleNamespace()), pytest.raises(SystemExit) as error:
        _ = app.sync

    assert 'No class "FtpClient"' in str(error.value)


def test_sync_wraps_client_initialization_errors(app):
    transfer_client = MagicMock(side_effect=RuntimeError("initialization failed"))
    app.config["SEEDBOXSYNC_SEEDBOX_PROTOCOL"] = "sftp"

    with patch("seedboxsync.core.flask.import_module", return_value=SimpleNamespace(SftpClient=transfer_client)), pytest.raises(ConnectionError) as error:
        _ = app.sync

    assert "initialization failed" in str(error.value)
    assert "Failed to establish a connection" in str(error.value)


def test_ping_client_is_loaded_and_cached(app):
    ping_client = MagicMock(return_value=object())

    with patch("seedboxsync.core.flask.import_module", return_value=SimpleNamespace(Healthchecks=ping_client)) as import_module:
        first = app.ping
        second = app.ping

    assert first is second
    import_module.assert_called_once_with("seedboxsync.core.ping.client.healthchecks")
    ping_client.assert_called_once_with()


def test_ping_reports_import_and_class_errors(app):
    with patch("seedboxsync.core.flask.import_module", side_effect=ImportError("missing")), pytest.raises(SystemExit) as import_error:
        _ = app.ping
    assert "Unsupported ping service: healthchecks" in str(import_error.value)

    app.__dict__.pop("ping", None)
    with patch("seedboxsync.core.flask.import_module", return_value=SimpleNamespace()), pytest.raises(SystemExit) as class_error:
        _ = app.ping
    assert 'No class "Healthchecks"' in str(class_error.value)


def test_task_manager_is_initialized_once_and_cached(app):
    manager = MagicMock()

    with patch("seedboxsync.core.flask.task_manager", manager):
        first = app.task_manager
        second = app.task_manager

    assert first is manager
    assert second is manager
    manager.init_app.assert_called_once_with(app)
