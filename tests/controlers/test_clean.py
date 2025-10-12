import pytest
from tests.main import SeedboxSyncTest, hash_output


def test_seedboxsync_clean(tmp):
    """
    Test clean command.
    """

    _, tmp_config_files, _, _ = tmp

    # seedboxsync clean -h (SystemExit 0)
    argv = ['clean', '-h']
    with pytest.raises(SystemExit) as excinfo:
        with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
            app.run()
    assert excinfo.value.code == 0


def test_seedboxsync_clean_progress(tmp):
    """
    Test clean progress command.
    """

    _, tmp_config_files, _, _ = tmp

    # seedboxsync clean progress -h (SystemExit 0)
    argv = ['clean', 'progress', '-h']
    with pytest.raises(SystemExit) as excinfo:
        with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
            app.run()
    assert excinfo.value.code == 0

    # seedboxsync clean progress
    argv = ['clean', 'progress']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        _, output = app.last_rendered
        assert hash_output(output) == 'e8a1eb752a7fb6607ec41e63aaf45ebf'


def test_seedboxsync_clean_downloaded(tmp):
    """
    Test clean downloaded command.
    """

    _, tmp_config_files, _, _ = tmp

    # seedboxsync clean downloaded (SystemExit 2)
    argv = ['clean', 'downloaded']
    with pytest.raises(SystemExit) as excinfo:
        with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
            app.run()
    assert excinfo.value.code == 2

    # seedboxsync clean downloaded -h (SystemExit 0)
    argv = ['clean', 'downloaded', '-h']
    with pytest.raises(SystemExit) as excinfo:
        with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
            app.run()
    assert excinfo.value.code == 0

    # seedboxsync clean downloaded 607
    argv = ['clean', 'downloaded', '607']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        _, output = app.last_rendered
        assert hash_output(output) == '48d2b91a68900eef6fc440546c305830'

    # seedboxsync clean downloaded 9999
    argv = ['clean', 'downloaded', '9999']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        _, output = app.last_rendered
        assert hash_output(output) == '2fee9806c05cddcd334cbce9cbd922af'
