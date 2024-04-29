import hashlib
import os
from seedboxsync.main import SeedboxSyncTest


config_dirs = [os.getcwd() + '/tests/resources']


def test_seedboxsync_search_downloaded():
    """
    Test search downloaded command.
    """

    # seedboxsync search downloaded
    argv = ['search', 'downloaded']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == '7f5b9b8878af179e872b8110382cde4a'

    # seedboxsync search downloaded -n 5
    argv = ['search', 'downloaded', '-n', '5']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == '319d69087d3a3273b44a4546a137a9fc'


def test_seedboxsync_search_progress():
    """
    Test search progress command.
    """

    # seedboxsync search progress
    argv = ['search', 'progress']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == 'af0cf1e7182c2f7bc64f30ccf5bfa00a'

    # seedboxsync search progress -n 1
    argv = ['search', 'progress', '-n', '1']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == 'b4e4872e2831f30392f7301eb44dbf01'


def test_seedboxsync_search_uploaded():
    """
    Test search uploaded command.
    """

    # seedboxsync search uploaded
    argv = ['search', 'uploaded']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == 'eddf5be7df1164d0e13da4df497a8ce3'

    # seedboxsync search uploaded -n 5
    argv = ['search', 'uploaded', '-n', '5']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == 'd9da6c5c513564702263eb84417c133a'
