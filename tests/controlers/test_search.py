import pytest
from tests.main import SeedboxSyncTest, hash_output


def test_seedboxsync_search(tmp):
    """
    Test search command.
    """

    _, tmp_config_files, _, _ = tmp

    # seedboxsync search -h
    argv = ['search', '-h']
    with pytest.raises(SystemExit) as excinfo:
        with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
            app.run()
    assert excinfo.value.code == 0


def test_seedboxsync_search_downloaded(tmp):
    """
    Test search downloaded command.
    """

    _, tmp_config_files, _, _ = tmp

    # seedboxsync search downloaded -h
    argv = ['search', 'downloaded', '-h']
    with pytest.raises(SystemExit) as excinfo:
        with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
            app.run()
    assert excinfo.value.code == 0

    # seedboxsync search downloaded
    argv = ['search', 'downloaded']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        _, output = app.last_rendered
        assert hash_output(output) == '7429e74cb0dbd512b65ba53949410bed'

    # seedboxsync search downloaded -n 5
    argv = ['search', 'downloaded', '-n', '5']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        _, output = app.last_rendered
        assert hash_output(output) == '9e72e4a8b98c1a63f7f438c46ba1616b'
    # seedboxsync search downloaded --number 5
    argv = ['search', 'downloaded', '--number', '5']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        _, output = app.last_rendered
        assert hash_output(output) == '9e72e4a8b98c1a63f7f438c46ba1616b'

    # seedboxsync search downloaded -s Nulla
    argv = ['search', 'downloaded', '-s', 'Nulla']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        _, output = app.last_rendered
        assert hash_output(output) == '5831e9dc3c21b6b35715f0b7a8f84b5f'
    # seedboxsync search downloaded --search 5
    argv = ['search', 'downloaded', '--search', 'nULLa']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        _, output = app.last_rendered
        assert hash_output(output) == '5831e9dc3c21b6b35715f0b7a8f84b5f'


def test_seedboxsync_search_progress(tmp):
    """
    Test search progress command.
    """

    _, tmp_config_files, _, _ = tmp

    # seedboxsync search progress -h
    argv = ['search', 'progress', '-h']
    with pytest.raises(SystemExit) as excinfo:
        with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
            app.run()
    assert excinfo.value.code == 0

    # seedboxsync search progress
    argv = ['search', 'progress']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        _, output = app.last_rendered
        assert hash_output(output) == 'e3bed24f4245f631d94668d67f511f7f'

    # seedboxsync search progress -n 1
    argv = ['search', 'progress', '-n', '1']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        _, output = app.last_rendered
        assert hash_output(output) == 'bfa0b491cd08f37d6024de7f1ec09e93'
    # seedboxsync search progress --number 1
    argv = ['search', 'progress', '--number', '1']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        _, output = app.last_rendered
        assert hash_output(output) == 'bfa0b491cd08f37d6024de7f1ec09e93'

    # seedboxsync search progress -s ante
    argv = ['search', 'progress', '-s', 'smor']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        _, output = app.last_rendered
        assert hash_output(output) == 'bfa0b491cd08f37d6024de7f1ec09e93'
    # seedboxsync search progress --search AnTe
    argv = ['search', 'progress', '--search', 'sMor']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        _, output = app.last_rendered
        assert hash_output(output) == 'bfa0b491cd08f37d6024de7f1ec09e93'


def test_seedboxsync_search_uploaded(tmp):
    """
    Test search uploaded command.
    """

    _, tmp_config_files, _, _ = tmp

    # seedboxsync search uploaded -h
    argv = ['search', 'uploaded', '-h']
    with pytest.raises(SystemExit) as excinfo:
        with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
            app.run()
    assert excinfo.value.code == 0

    # seedboxsync search uploaded
    argv = ['search', 'uploaded']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        _, output = app.last_rendered
        assert hash_output(output) == 'eddf5be7df1164d0e13da4df497a8ce3'

    # seedboxsync search uploaded -n 5
    argv = ['search', 'uploaded', '-n', '5']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        _, output = app.last_rendered
        assert hash_output(output) == 'd9da6c5c513564702263eb84417c133a'
    # seedboxsync search uploaded --number 5
    argv = ['search', 'uploaded', '--number', '5']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        _, output = app.last_rendered
        assert hash_output(output) == 'd9da6c5c513564702263eb84417c133a'

    # seedboxsync search uploaded -s Vol
    argv = ['search', 'uploaded', '-s', 'Vol']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        _, output = app.last_rendered
        assert hash_output(output) == '674e18ee2dac8f603524d90d21131631'
    # seedboxsync search uploaded --search vOl
    argv = ['search', 'uploaded', '--search', 'Vol']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        _, output = app.last_rendered
        assert hash_output(output) == '674e18ee2dac8f603524d90d21131631'
