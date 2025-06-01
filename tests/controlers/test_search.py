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
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == 'd5358298b49cb0359b379000d215ec41'

    # seedboxsync search downloaded -n 5
    argv = ['search', 'downloaded', '-n', '5']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == '013c431a1bf733bfb3108d3e692ff9c8'
    # seedboxsync search downloaded --number 5
    argv = ['search', 'downloaded', '--number', '5']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == '013c431a1bf733bfb3108d3e692ff9c8'

    # seedboxsync search downloaded -s Nulla
    argv = ['search', 'downloaded', '-s', 'Nulla']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == '6f8c477b46b38e1c87aa5af21b95a67c'
    # seedboxsync search downloaded --search 5
    argv = ['search', 'downloaded', '--search', 'nULLa']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == '6f8c477b46b38e1c87aa5af21b95a67c'


def test_seedboxsync_search_progress():
    """
    Test search progress command.
    """

    # seedboxsync search progress
    argv = ['search', 'progress']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == 'e776b53155595b6cc66bd21e6c16a547'

    # seedboxsync search progress -n 1
    argv = ['search', 'progress', '-n', '1']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == '892f588b5a6b2b45a29a40ec61a43465'
    # seedboxsync search progress --number 1
    argv = ['search', 'progress', '--number', '1']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == '892f588b5a6b2b45a29a40ec61a43465'

    # seedboxsync search progress -s ante
    argv = ['search', 'progress', '-s', 'smor']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == '892f588b5a6b2b45a29a40ec61a43465'
    # seedboxsync search progress --search AnTe
    argv = ['search', 'progress', '--search', 'sMor']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == '892f588b5a6b2b45a29a40ec61a43465'


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
