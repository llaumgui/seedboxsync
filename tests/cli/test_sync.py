from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, PropertyMock, patch
import pytest
from seedboxsync.cli import cli
from seedboxsync.core.dao import Download, TaskStatus, Torrent
from seedboxsync.core.flask import SeedboxSyncFlask


@pytest.fixture
def sync_services():
    sync = MagicMock()
    ping = MagicMock()
    with (
        patch.object(SeedboxSyncFlask, "sync", new_callable=PropertyMock, return_value=sync),
        patch.object(SeedboxSyncFlask, "ping", new_callable=PropertyMock, return_value=ping),
    ):
        yield sync, ping


def test_sync_help_lists_both_workflows(runner):
    result = runner.invoke(cli, ["sync", "--help"])

    assert result.exit_code == 0
    assert "blackhole" in result.output
    assert "seedbox" in result.output


@pytest.mark.parametrize("command, config_key", [("blackhole", "SEEDBOXSYNC_SYNC_BLACKHOLE_ENABLED"), ("seedbox", "SEEDBOXSYNC_SYNC_SEEDBOX_ENABLED")])
def test_disabled_sync_exits_without_initializing_network_client(app, runner, command, config_key):
    app.config[config_key] = False

    with patch.object(SeedboxSyncFlask, "sync", new_callable=PropertyMock) as get_sync:
        result = runner.invoke(cli, ["sync", command])

    assert result.exit_code == 0
    get_sync.assert_not_called()


def test_blackhole_uploads_and_records_torrent(app, runner, tmp_path, sync_services):
    sync, ping = sync_services
    watch_dir = tmp_path / "watch"
    watch_dir.mkdir()
    torrent_file = watch_dir / "release.torrent"
    torrent_file.write_bytes(b"torrent data")
    app.config.update(
        SEEDBOXSYNC_SYNC_BLACKHOLE_ENABLED=True,
        SEEDBOXSYNC_LOCAL_WATCH_PATH=str(watch_dir),
        SEEDBOXSYNC_SEEDBOX_TMP_PATH="/remote/tmp",
        SEEDBOXSYNC_SEEDBOX_WATCH_PATH="/remote/watch",
        SEEDBOXSYNC_SEEDBOX_CHMOD="0640",
    )

    with patch("seedboxsync.core.utils.get_torrent_infos", return_value={"announce": "https://tracker.example/announce"}):
        result = runner.invoke(cli, ["sync", "blackhole", "--ping"])

    assert result.exit_code == 0, result.output
    assert not torrent_file.exists()
    sync.put.assert_called_once_with(Path(torrent_file), Path("/remote/tmp/release.torrent"))
    sync.chmod.assert_called_once_with(Path("/remote/tmp/release.torrent"), 0o640)
    sync.rename.assert_called_once_with(Path("/remote/tmp/release.torrent"), Path("/remote/watch/release.torrent"))
    ping.start.assert_called_once_with("sync_blackhole")
    ping.success.assert_called_once_with("sync_blackhole")
    with app.app_context():
        torrent = Torrent.get(Torrent.name == "release.torrent")
        assert torrent.announce == "https://tracker.example/announce"
        status = TaskStatus.get_by_id("sync-blackhole")
        assert status.running is False
        assert status.finished is not None


def test_blackhole_dry_run_keeps_file_and_database_unchanged(app, runner, tmp_path, sync_services):
    sync, ping = sync_services
    watch_dir = tmp_path / "watch"
    watch_dir.mkdir()
    torrent_file = watch_dir / "dry-run.torrent"
    torrent_file.write_bytes(b"untouched")
    app.config.update(SEEDBOXSYNC_SYNC_BLACKHOLE_ENABLED=True, SEEDBOXSYNC_LOCAL_WATCH_PATH=str(watch_dir))

    result = runner.invoke(cli, ["sync", "blackhole", "--dry-run"])

    assert result.exit_code == 0
    assert torrent_file.exists()
    sync.put.assert_not_called()
    ping.start.assert_not_called()
    ping.success.assert_not_called()
    with app.app_context():
        assert Torrent.select().where(Torrent.name == "dry-run.torrent").count() == 0


def test_blackhole_marks_invalid_torrent_as_failed(app, runner, tmp_path, sync_services):
    watch_dir = tmp_path / "watch"
    watch_dir.mkdir()
    torrent_file = watch_dir / "invalid.torrent"
    torrent_file.write_bytes(b"invalid")
    app.config.update(
        SEEDBOXSYNC_SYNC_BLACKHOLE_ENABLED=True,
        SEEDBOXSYNC_LOCAL_WATCH_PATH=str(watch_dir),
        SEEDBOXSYNC_SEEDBOX_TMP_PATH="/tmp",
        SEEDBOXSYNC_SEEDBOX_WATCH_PATH="/watch",
    )

    with patch("seedboxsync.core.utils.get_torrent_infos", return_value=None):
        result = runner.invoke(cli, ["sync", "blackhole"])

    assert result.exit_code == 0
    assert not torrent_file.exists()
    assert Path(f"{torrent_file}.fail").exists()


def test_seedbox_only_store_records_remote_file_without_downloading(app, runner, sync_services):
    sync, ping = sync_services
    sync.walk.return_value = [("shows", [], ["episode.mkv", "partial.part"])]
    sync.stat.return_value = SimpleNamespace(st_size=4096)
    app.config.update(
        SEEDBOXSYNC_SYNC_SEEDBOX_ENABLED=True,
        SEEDBOXSYNC_SEEDBOX_FINISHED_PATH="/remote/files",
        SEEDBOXSYNC_SEEDBOX_PART_SUFFIX=".part",
        SEEDBOXSYNC_SEEDBOX_EXCLUDE_SYNCING="",
    )

    result = runner.invoke(cli, ["sync", "seedbox", "--only-store", "--ping"])

    assert result.exit_code == 0, result.output
    sync.stat.assert_called_once_with("shows/episode.mkv")
    sync.get.assert_not_called()
    ping.start.assert_called_once_with("sync_seedbox")
    ping.success.assert_called_once_with("sync_seedbox")
    with app.app_context():
        download = Download.get(Download.path == "shows/episode.mkv")
        assert download.seedbox_size == 4096
        assert download.local_size == 4096
        assert download.finished != 0
        assert Download.select().where(Download.path.endswith("partial.part")).count() == 0


def test_seedbox_download_writes_and_renames_part_file(app, runner, tmp_path, sync_services):
    sync, _ = sync_services
    sync.walk.return_value = [("", [], ["movie.mkv"])]
    sync.stat.return_value = SimpleNamespace(st_size=7)

    def write_download(_remote_path, local_path, progress_callback):
        Path(local_path).write_bytes(b"content")
        progress_callback(7, 7)

    sync.get.side_effect = write_download
    app.config.update(
        SEEDBOXSYNC_SYNC_SEEDBOX_ENABLED=True,
        SEEDBOXSYNC_SEEDBOX_FINISHED_PATH="/remote/files",
        SEEDBOXSYNC_SEEDBOX_PART_SUFFIX=".part",
        SEEDBOXSYNC_SEEDBOX_EXCLUDE_SYNCING="",
        SEEDBOXSYNC_LOCAL_DOWNLOAD_PATH=str(tmp_path / "downloads"),
    )

    result = runner.invoke(cli, ["sync", "seedbox"])

    assert result.exit_code == 0, result.output
    downloaded_file = tmp_path / "downloads" / "movie.mkv"
    assert downloaded_file.read_bytes() == b"content"
    assert not Path(f"{downloaded_file}.part").exists()
    with app.app_context():
        download = Download.get(Download.path == "movie.mkv")
        assert download.local_size == 7
        assert download.finished != 0


def test_seedbox_skips_excluded_and_already_downloaded_files(app, runner, sync_services):
    sync, _ = sync_services
    sync.walk.return_value = [("", [], ["existing.mkv", "sample.mkv", "keep.mkv"])]
    sync.stat.return_value = SimpleNamespace(st_size=10)
    app.config.update(
        SEEDBOXSYNC_SYNC_SEEDBOX_ENABLED=True,
        SEEDBOXSYNC_SEEDBOX_FINISHED_PATH="/remote/files",
        SEEDBOXSYNC_SEEDBOX_PART_SUFFIX=".part",
        SEEDBOXSYNC_SEEDBOX_EXCLUDE_SYNCING="sample",
    )
    with app.app_context():
        Download.create(path="existing.mkv", seedbox_size=10, local_size=10, finished="2026-01-01")

    result = runner.invoke(cli, ["sync", "seedbox", "--only-store"])

    assert result.exit_code == 0
    sync.stat.assert_called_once_with("keep.mkv")
    with app.app_context():
        assert Download.select().where(Download.path == "existing.mkv").count() == 1
        assert Download.select().where(Download.path == "sample.mkv").count() == 0
        assert Download.select().where(Download.path == "keep.mkv").count() == 1


def test_seedbox_rejects_invalid_exclusion_regex(app, runner, sync_services):
    sync, _ = sync_services
    sync.walk.return_value = [("", [], ["file.mkv"])]
    app.config.update(
        SEEDBOXSYNC_SYNC_SEEDBOX_ENABLED=True,
        SEEDBOXSYNC_SEEDBOX_FINISHED_PATH="/remote/files",
        SEEDBOXSYNC_SEEDBOX_PART_SUFFIX=".part",
        SEEDBOXSYNC_SEEDBOX_EXCLUDE_SYNCING="[",
    )

    result = runner.invoke(cli, ["sync", "seedbox"])

    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
    assert "Invalid configuration for exclude_syncing" in str(result.exception)
