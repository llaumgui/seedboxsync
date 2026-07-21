import socket
import stat
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import paramiko
import pytest
from seedboxsync.core.sync.client.sftp import SftpClient


@pytest.fixture
def sftp_app(app):
    app.config.update(
        SEEDBOXSYNC_SEEDBOX_HOST="my-seedbox.ltd",
        SEEDBOXSYNC_SEEDBOX_PORT="2222",
        SEEDBOXSYNC_SEEDBOX_LOGIN="me",
        SEEDBOXSYNC_SEEDBOX_PASSWORD="p@ssword",
        SEEDBOXSYNC_SEEDBOX_TIMEOUT=False,
        SEEDBOXSYNC_SEEDBOX_MAX_CONCURRENT_PREFETCH_REQUESTS="16",
    )
    return app


@pytest.fixture
def paramiko_mocks():
    transport = MagicMock()
    transport.is_active.return_value = True
    client = MagicMock()
    with (
        patch("seedboxsync.core.sync.client.sftp.paramiko.Transport", return_value=transport) as transport_factory,
        patch("seedboxsync.core.sync.client.sftp.paramiko.SFTPClient.from_transport", return_value=client) as client_factory,
    ):
        yield transport_factory, transport, client_factory, client


def test_client_initialization_is_lazy_and_reads_configuration(sftp_app):
    with patch("seedboxsync.core.sync.client.sftp.paramiko.Transport") as transport_factory, sftp_app.app_context():
        client = SftpClient()

        assert client._host == "my-seedbox.ltd"
        assert client._port == "2222"
        assert client._login == "me"
        assert client._max_concurrent_prefetch_requests == 16
        assert client._transport is None
        transport_factory.assert_not_called()


def test_put_opens_connection_once_and_uploads_file(sftp_app, paramiko_mocks):
    transport_factory, transport, client_factory, sftp = paramiko_mocks
    uploaded_attributes = object()
    sftp.put.return_value = uploaded_attributes

    with sftp_app.app_context():
        client = SftpClient()
        result = client.put("/local/file.torrent", "/remote/file.torrent")
        client.stat("/remote/file.torrent")

    assert result is uploaded_attributes
    transport_factory.assert_called_once_with(("my-seedbox.ltd", 2222))
    transport.connect.assert_called_once_with(username="me", password="p@ssword")
    client_factory.assert_called_once_with(transport)
    sftp.put.assert_called_once_with("/local/file.torrent", "/remote/file.torrent")
    sftp.stat.assert_called_once_with("/remote/file.torrent")


def test_get_forwards_callback_and_prefetch_limit(sftp_app, paramiko_mocks):
    _, _, _, sftp = paramiko_mocks
    callback = MagicMock()

    with sftp_app.app_context():
        SftpClient().get("/remote/movie.mkv", "/local/movie.mkv", progress_callback=callback)

    sftp.get.assert_called_once_with(
        "/remote/movie.mkv",
        "/local/movie.mkv",
        callback=callback,
        max_concurrent_prefetch_requests=16,
    )


def test_configured_timeout_is_applied_to_sftp_channel(sftp_app, paramiko_mocks):
    _, _, _, sftp = paramiko_mocks
    channel = sftp.get_channel.return_value
    channel.gettimeout.return_value = 30
    sftp_app.config["SEEDBOXSYNC_SEEDBOX_TIMEOUT"] = 30

    with sftp_app.app_context():
        SftpClient().chdir("/files")

    channel.settimeout.assert_called_once_with(30)
    sftp.chdir.assert_called_once_with("/files")


def test_file_operations_are_delegated_to_paramiko(sftp_app, paramiko_mocks):
    transport_factory, _, _, sftp = paramiko_mocks

    with sftp_app.app_context():
        client = SftpClient()
        client.chdir(None)
        client.chmod("/remote/file", 0o640)
        client.rename("/remote/old", "/remote/new")

    transport_factory.assert_called_once()
    sftp.chdir.assert_called_once_with(None)
    sftp.chmod.assert_called_once_with("/remote/file", 0o640)
    sftp.posix_rename.assert_called_once_with("/remote/old", "/remote/new")


def test_rename_also_initializes_a_lazy_connection(sftp_app, paramiko_mocks):
    transport_factory, _, _, sftp = paramiko_mocks

    with sftp_app.app_context():
        SftpClient().rename("old", "new")

    transport_factory.assert_called_once_with(("my-seedbox.ltd", 2222))
    sftp.posix_rename.assert_called_once_with("old", "new")


def test_walk_recurses_into_remote_directories(sftp_app, paramiko_mocks):
    _, _, _, sftp = paramiko_mocks
    folder = SimpleNamespace(filename="season", st_mode=stat.S_IFDIR | 0o755)
    root_file = SimpleNamespace(filename="cover.jpg", st_mode=stat.S_IFREG | 0o644)
    episode = SimpleNamespace(filename="episode.mkv", st_mode=stat.S_IFREG | 0o644)
    sftp.listdir_attr.side_effect = [[folder, root_file], [episode]]

    with sftp_app.app_context():
        result = list(SftpClient().walk("shows"))

    assert result == [
        ("shows", ["season"], ["cover.jpg"]),
        ("shows/season", [], ["episode.mkv"]),
    ]
    assert sftp.listdir_attr.call_args_list[0].args == ("shows",)
    assert sftp.listdir_attr.call_args_list[1].args == ("shows/season",)


def test_close_is_safe_before_connection_and_closes_connected_transport(sftp_app, paramiko_mocks):
    _, transport, _, _ = paramiko_mocks

    with sftp_app.app_context():
        client = SftpClient()
        client.close()
        transport.close.assert_not_called()

        client.chdir("/files")
        client.close()

    transport.close.assert_called_once_with()


def test_inactive_transport_is_closed_and_replaced(sftp_app):
    inactive_transport = MagicMock()
    inactive_transport.is_active.return_value = False
    replacement_transport = MagicMock()
    replacement_transport.is_active.return_value = True
    first_sftp = MagicMock()
    replacement_sftp = MagicMock()

    with (
        patch(
            "seedboxsync.core.sync.client.sftp.paramiko.Transport",
            side_effect=[inactive_transport, replacement_transport],
        ) as transport_factory,
        patch(
            "seedboxsync.core.sync.client.sftp.paramiko.SFTPClient.from_transport",
            side_effect=[first_sftp, replacement_sftp],
        ) as client_factory,
        sftp_app.app_context(),
    ):
        client = SftpClient()
        client.chdir("/first")
        client.chdir("/second")

    assert transport_factory.call_count == 2
    assert client_factory.call_args_list[0].args == (inactive_transport,)
    assert client_factory.call_args_list[1].args == (replacement_transport,)
    inactive_transport.close.assert_called_once_with()
    first_sftp.chdir.assert_called_once_with("/first")
    replacement_sftp.chdir.assert_called_once_with("/second")


def test_connection_failure_is_reported_without_creating_sftp_client(sftp_app):
    with (
        patch("seedboxsync.core.sync.client.sftp.paramiko.Transport", side_effect=socket.gaierror("host not found")),
        patch("seedboxsync.core.sync.client.sftp.paramiko.SFTPClient.from_transport") as client_factory,
        sftp_app.app_context(),
        pytest.raises(SystemExit) as error,
    ):
        SftpClient().chdir("/files")

    assert "Failed to establish a connection" in str(error.value)
    assert "host and port are correct" in str(error.value)
    client_factory.assert_not_called()


def test_authentication_failure_is_reported(sftp_app, paramiko_mocks):
    _, transport, client_factory, _ = paramiko_mocks
    transport.connect.side_effect = paramiko.AuthenticationException("authentication failed")

    with sftp_app.app_context(), pytest.raises(SystemExit) as error:
        SftpClient().chdir("/files")

    assert "Ensure the login and password are correct" in str(error.value)
    client_factory.assert_not_called()
