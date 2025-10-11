import pytest
from tests.main import SeedboxSyncTest
from os.path import isfile
from seedboxsync.core.dao.torrent import Torrent
from peewee import fn


def test_seedboxsync_sync():
    """
    Test sync command.
    """

    # seedboxsync sync -h (SystemExit 0)
    argv = ['sync', '-h']
    with pytest.raises(SystemExit) as excinfo:
        with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
            app.run()
    assert excinfo.value.code == 0


def test_seedboxsync_sync_blackhole(capsys, mock_sftp):
    """
    Test sync blackhole command.
    """

    # seedboxsync sync blackhole -h (SystemExit 0)
    argv = ['sync', 'blackhole', '-h']
    with pytest.raises(SystemExit) as excinfo:
        with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
            app.run()
    assert excinfo.value.code == 0

    # seedboxsync sync blackhole (with empty watch folder)
    SeedboxSyncTest.backup_and_clean_watch()
    try:
        argv = ['sync', 'blackhole']
        with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
            app.run()
            output = capsys.readouterr().err
            assert app.exit_code == 0
            assert 'No torrent files found in ' in output
    finally:
        SeedboxSyncTest.restore_watch()

    # seedboxsync sync blackhole
    SeedboxSyncTest.backup_watch()
    try:
        argv = ['sync', 'blackhole']
        with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
            app.run()
            output = capsys.readouterr().err
            assert app.exit_code == 0  # No error code
            assert SeedboxSyncTest.hash_output(output) == 'f93396c51a8ae2b40b2390aee0c1cb42'  # Message is good
            assert not isfile(SeedboxSyncTest.get_watch_torrent_path())  # Torrent file is removed
            uploaded = Torrent.select(fn.COUNT(Torrent.id).alias('count')).where(Torrent.name.contains('Fedora-Server-dvd-x86_64-32'))
            count = uploaded.scalar()
            assert count == 1  # One torrent uploaded
    finally:
        SeedboxSyncTest.restore_watch()


def test_seedboxsync_sync_seedbox_with_empty_download(capsys, mock_sftp, mock_empty_download):
    """
    Test sync seedbox command.
    """

    # seedboxsync sync seedbox -h (SystemExit 0)
    argv = ['sync', 'seedbox', '-h']
    with pytest.raises(SystemExit) as excinfo:
        with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
            app.run()
    assert excinfo.value.code == 0

    # seedboxsync sync seedbox
    argv = ['sync', 'seedbox']
    with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
        app.run()
        output = capsys.readouterr().err
        print(output)
        assert app.exit_code == 0  # No error code
        assert output == ''
