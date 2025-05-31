import hashlib
import os
from seedboxsync.main import SeedboxSyncTest


config_dirs = [os.getcwd() + '/tests/resources']


def test_seedboxsync_stats_by_month():
    """
    Test stats command.
    """

    # seedboxsync stats by-month
    argv = ['stats', 'by-month']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:

        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == 'fd5bbe21431cfcfff81455804ad30629'

    # seedboxsync stats by-year
    argv = ['stats', 'by-year']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:

        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == 'ec263be8819b09693ffe82cd131e211e'
