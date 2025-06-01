import pytest
from tests.main import SeedboxSyncTest


def test_seedboxsync_clean():
    """
    Test clean command.
    """

    # seedboxsync clean -h (SystemExit 0)
    argv = ['clean', '-h']
    with pytest.raises(SystemExit) as excinfo:
        with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
            app.run()
    assert excinfo.value.code == 0


def test_seedboxsync_clean_progress():
    """
    Test clean command.
    """

    # Begin: backup DB
    SeedboxSyncTest.backup_db()

    # seedboxsync clean progress -h (SystemExit 0)
    argv = ['clean', 'progress', '-h']
    with pytest.raises(SystemExit) as excinfo:
        with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
            app.run()
    assert excinfo.value.code == 0

    # Operation on database
    try:
        # seedboxsync clean progress
        argv = ['clean', 'progress']
        with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
            app.run()
            data, output = app.last_rendered
            assert SeedboxSyncTest.hash_output(output) == 'e8a1eb752a7fb6607ec41e63aaf45ebf'
    finally:
        # End: restore DB
        SeedboxSyncTest.restore_db()


def test_seedboxsync_clean_downloaded():
    """
    Test clean command.
    """

    # Begin: ackup DB
    SeedboxSyncTest.backup_db()

    help

    # seedboxsync clean downloaded (SystemExit 2)
    argv = ['clean', 'downloaded']
    with pytest.raises(SystemExit) as excinfo:
        with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
            app.run()
    assert excinfo.value.code == 2

    # seedboxsync clean downloaded -h (SystemExit 0)
    argv = ['clean', 'downloaded', '-h']
    with pytest.raises(SystemExit) as excinfo:
        with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
            app.run()
    assert excinfo.value.code == 0

    # Operation on database
    try:
        # seedboxsync clean downloaded 607
        argv = ['clean', 'downloaded', '607']
        with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
            app.run()
            data, output = app.last_rendered
            assert SeedboxSyncTest.hash_output(output) == '48d2b91a68900eef6fc440546c305830'

        # seedboxsync clean downloaded 9999
        argv = ['clean', 'downloaded', '9999']
        with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
            app.run()
            data, output = app.last_rendered
            assert SeedboxSyncTest.hash_output(output) == '2fee9806c05cddcd334cbce9cbd922af'
    finally:
        # End: restore DB
        SeedboxSyncTest.restore_db()
