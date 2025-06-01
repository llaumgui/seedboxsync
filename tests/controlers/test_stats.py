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
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == '5bdf7b91831435e54b7d07fa0f2655f0'

    # seedboxsync stats by-year
    argv = ['stats', 'by-year']
    with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
        app.run()
        data, output = app.last_rendered
        assert hashlib.md5(output.encode('utf-8')).hexdigest() == '442aad79ee2a0b24ca777f548a7186d5'
