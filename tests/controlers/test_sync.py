import pytest
from tests.main import SeedboxSyncTest


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


def test_seedboxsync_sync_blackhole(capsys):
    """
    Test sync command.
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
            assert 'No torrent in ' in output
    finally:
        SeedboxSyncTest.restore_watch()
        print()


def test_seedboxsync_sync_seedbox():
    """
    Test sync command.
    """

    # seedboxsync sync seedbox -h (SystemExit 0)
    argv = ['sync', 'seedbox', '-h']
    with pytest.raises(SystemExit) as excinfo:
        with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
            app.run()
    assert excinfo.value.code == 0
