from unittest.mock import MagicMock, call, patch

import pytest

from seedboxsync.core.sync.client.ftp import FtpClient, FtpSession


@pytest.fixture
def ftp_app(app):
    app.config.update(
        SEEDBOXSYNC_SEEDBOX_HOST="my-seedbox.ltd",
        SEEDBOXSYNC_SEEDBOX_PORT="2121",
        SEEDBOXSYNC_SEEDBOX_LOGIN="me",
        SEEDBOXSYNC_SEEDBOX_PASSWORD="p@ssword",
        SEEDBOXSYNC_SEEDBOX_TIMEOUT=False,
    )
    return app


@pytest.fixture
def ftp_mocks():
    ftp = MagicMock()
    ftp.curdir = "/home/me"
    ftp.sep = "/"
    with patch("seedboxsync.core.sync.client.ftp.ftputil.FTPHost", return_value=ftp) as ftp_host:
        yield ftp_host, ftp


def test_ftp_session_connects_and_authenticates_with_custom_settings():
    with patch("seedboxsync.core.sync.client.ftp.ftplib.FTP.connect") as connect, patch("seedboxsync.core.sync.client.ftp.ftplib.FTP.login") as login:
        FtpSession("my-seedbox.ltd", "me", "p@ssword", port=2121, timeout=12.5)

    connect.assert_called_once_with("my-seedbox.ltd", 2121, timeout=12.5)
    login.assert_called_once_with("me", "p@ssword")


def test_client_initialization_is_lazy_and_reads_configuration(ftp_app):
    with patch("seedboxsync.core.sync.client.ftp.ftputil.FTPHost") as ftp_host, ftp_app.app_context():
        client = FtpClient()

        assert client._host == "my-seedbox.ltd"
        assert client._port == "2121"
        assert client._login == "me"
        assert client._client is None
        ftp_host.assert_not_called()


@pytest.mark.parametrize(
    ("configured", "expected"),
    [
        (False, None),
        (None, None),
        ("", None),
        ("false", None),
        ("NONE", None),
        ("null", None),
        ("12.5", 12.5),
        (30, 30.0),
        (2.5, 2.5),
    ],
)
def test_timeout_normalization(ftp_app, configured, expected):
    ftp_app.config["SEEDBOXSYNC_SEEDBOX_TIMEOUT"] = configured

    with ftp_app.app_context():
        assert FtpClient()._normalize_timeout() == expected


def test_get_without_callback_uses_ftputil_download(ftp_app, ftp_mocks):
    _, ftp = ftp_mocks

    with ftp_app.app_context():
        FtpClient().get("/remote/movie.mkv", "/local/movie.mkv")

    ftp.download.assert_called_once_with("/remote/movie.mkv", "/local/movie.mkv")
    ftp._session.retrbinary.assert_not_called()


def test_get_with_callback_streams_file_and_reports_progress(ftp_app, ftp_mocks, tmp_path):
    _, ftp = ftp_mocks
    ftp.stat.return_value.st_size = 6
    callback = MagicMock()
    destination = tmp_path / "movie.mkv"

    def stream(_command, on_block):
        on_block(b"ab")
        on_block(b"cdef")

    ftp._session.retrbinary.side_effect = stream

    with ftp_app.app_context():
        FtpClient().get("/remote/movie.mkv", str(destination), progress_callback=callback)

    assert destination.read_bytes() == b"abcdef"
    ftp._session.retrbinary.assert_called_once()
    assert ftp._session.retrbinary.call_args.args[0] == "RETR /remote/movie.mkv"
    assert callback.call_args_list == [call(2, 6), call(6, 6)]


def test_walk_preserves_explicit_remote_paths(ftp_app, ftp_mocks):
    _, ftp = ftp_mocks
    ftp.walk.return_value = [("shows", ["season"], ["cover.jpg"]), ("shows/season", [], ["episode.mkv"])]

    with ftp_app.app_context():
        result = list(FtpClient().walk("shows"))

    assert result == ftp.walk.return_value
    ftp.walk.assert_called_once_with("shows")


def test_walk_from_current_directory_returns_sftp_compatible_paths(ftp_app, ftp_mocks):
    _, ftp = ftp_mocks
    ftp.walk.return_value = [
        ("/home/me", ["shows"], ["cover.jpg"]),
        ("/home/me/shows", [], ["episode.mkv"]),
        ("outside", [], ["other.txt"]),
    ]

    with ftp_app.app_context():
        result = list(FtpClient().walk(""))

    assert result == [
        ("", ["shows"], ["cover.jpg"]),
        ("shows", [], ["episode.mkv"]),
        ("outside", [], ["other.txt"]),
    ]
    ftp.walk.assert_called_once_with("/home/me")


def test_close_is_safe_and_allows_reconnection(ftp_app, ftp_mocks):
    ftp_host, ftp = ftp_mocks

    with ftp_app.app_context():
        client = FtpClient()
        client.close()
        ftp.close.assert_not_called()

        client.chdir("/files")
        client.close()
        assert client._client is None
        client.chdir("/other")

    ftp.close.assert_called_once_with()
    assert ftp_host.call_count == 2


@pytest.mark.parametrize("connection_error", [OSError("network unreachable"), EOFError("closed"), ValueError("bad port")])
def test_connection_failures_are_reported(ftp_app, connection_error):
    with patch("seedboxsync.core.sync.client.ftp.ftputil.FTPHost", side_effect=connection_error), ftp_app.app_context(), pytest.raises(SystemExit) as error:
        FtpClient().chdir("/files")

    assert str(connection_error) in str(error.value)
    assert "Ensure the host, port, login and password are correct" in str(error.value)
