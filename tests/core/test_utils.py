from io import StringIO
from unittest.mock import patch
import pytest
from seedboxsync.core import utils


@pytest.mark.parametrize(
    ("value", "suffix", "expected"),
    [
        (0, "B", "0.0GiB"),
        (1024**3, "B", "1.0GiB"),
        (1.5 * 1024**3, "o", "1.5Gio"),
    ],
)
def test_byte_to_gi_formats_binary_gigabytes(value, suffix, expected):
    assert utils.byte_to_gi(value, suffix) == expected


def test_get_torrent_infos_decodes_file_content(tmp_path):
    torrent = tmp_path / "movie.torrent"
    torrent.write_bytes(b"torrent payload")
    decoded = {b"info": {b"name": b"movie.mkv"}}

    with patch("seedboxsync.core.utils.bdecode", return_value=decoded) as decode:
        assert utils.get_torrent_infos(str(torrent)) == decoded

    decode.assert_called_once_with(b"torrent payload")


def test_get_torrent_infos_logs_invalid_files(app, tmp_path):
    torrent = tmp_path / "invalid.torrent"
    torrent.write_bytes(b"invalid")

    with app.app_context(), patch("seedboxsync.core.utils.bdecode", side_effect=ValueError("invalid bencode")), patch.object(app.logger, "exception") as log:
        assert utils.get_torrent_infos(str(torrent)) is None

    log.assert_called_once_with("Not valid torrent")


@pytest.mark.parametrize(
    ("mountinfo", "cgroup", "dockerenv", "expected"),
    [
        ("overlay /var/lib/docker", "", False, True),
        ("ext4 /", "0::/kubepods/pod", False, True),
        ("ext4 /", "0::/user.slice", True, True),
        ("ext4 /", "0::/user.slice", False, False),
    ],
)
def test_is_running_in_docker_checks_runtime_markers(mountinfo, cgroup, dockerenv, expected):
    files = {
        "/proc/self/mountinfo": mountinfo,
        "/proc/1/cgroup": cgroup,
    }

    def exists(path):
        return str(path) in files or (str(path) == "/.dockerenv" and dockerenv)

    def open_file(path, *args, **kwargs):
        return StringIO(files[str(path)])

    with patch.object(utils.Path, "exists", exists), patch.object(utils.Path, "open", open_file):
        assert utils.is_running_in_docker() is expected


def test_healthcheck_url_prefers_explicit_environment_url(monkeypatch):
    monkeypatch.setenv("HEALTHCHECK_URL", "https://seedbox.example/")
    monkeypatch.setenv("BIND", "0.0.0.0:9000")

    assert utils.get_web_healthcheck_url() == "https://seedbox.example/healthcheck"


@pytest.mark.parametrize(
    ("bind", "expected"),
    [
        ("0.0.0.0:8000", "http://127.0.0.1:8000/healthcheck"),
        ("localhost:9000", "http://localhost:9000/healthcheck"),
        ("[::]:7000", "http://127.0.0.1:7000/healthcheck"),
    ],
)
def test_healthcheck_url_uses_http_compatible_bind(monkeypatch, bind, expected):
    monkeypatch.delenv("HEALTHCHECK_URL", raising=False)
    monkeypatch.setenv("BIND", bind)

    assert utils.get_web_healthcheck_url() == expected


@pytest.mark.parametrize("bind", ["unix:/run/seedboxsync.sock", "localhost"])
def test_healthcheck_url_rejects_unsupported_bind(monkeypatch, bind):
    monkeypatch.delenv("HEALTHCHECK_URL", raising=False)
    monkeypatch.setenv("BIND", bind)

    with pytest.raises(ValueError):
        utils.get_web_healthcheck_url()


@pytest.mark.parametrize(("in_docker", "port"), [(False, 5000), (True, 8000)])
def test_healthcheck_url_uses_runtime_default(monkeypatch, in_docker, port):
    monkeypatch.delenv("HEALTHCHECK_URL", raising=False)
    monkeypatch.delenv("BIND", raising=False)

    with patch("seedboxsync.core.utils.is_running_in_docker", return_value=in_docker):
        assert utils.get_web_healthcheck_url() == f"http://127.0.0.1:{port}/healthcheck"
