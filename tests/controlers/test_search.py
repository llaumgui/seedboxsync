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
    # seedboxsync search downloaded --number 5
    argv = ['search', 'downloaded', '--number', '5']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == '319d69087d3a3273b44a4546a137a9fc'

    # seedboxsync search downloaded -s Nulla
    argv = ['search', 'downloaded', '-s', 'Nulla']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == '766078235505717bc48981d14db3b0e3'
    # seedboxsync search downloaded --search 5
    argv = ['search', 'downloaded', '--search', 'nULLa']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == '766078235505717bc48981d14db3b0e3'


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
    # seedboxsync search progress --number 1
    argv = ['search', 'progress', '--number', '1']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == 'b4e4872e2831f30392f7301eb44dbf01'

    # seedboxsync search progress -s ante
    argv = ['search', 'progress', '-s', 'ante']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == '70d7a75d7e6dc46f094c26d894764205'
    # seedboxsync search progress --search AnTe
    argv = ['search', 'progress', '--search', 'AnTe']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == '70d7a75d7e6dc46f094c26d894764205'


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
    # seedboxsync search uploaded --number 5
    argv = ['search', 'uploaded', '--number', '5']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == 'd9da6c5c513564702263eb84417c133a'

    # seedboxsync search uploaded -s Vol
    argv = ['search', 'uploaded', '-s', 'Vol']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == '674e18ee2dac8f603524d90d21131631'
    # seedboxsync search uploaded --search vOl
    argv = ['search', 'uploaded', '--search', 'Vol']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == '674e18ee2dac8f603524d90d21131631'
