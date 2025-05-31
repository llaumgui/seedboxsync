import hashlib
import os
import shutil
from seedboxsync.main import SeedboxSyncTest


config_dirs = [os.getcwd() + '/tests/resources']
db_path = config_dirs[0] + '/seedboxsync.db'
db_backup = db_path + '.bak'


def test_seedboxsync_stats_by_month():
    """
    Test stats command.
    """

    # Save database
    shutil.copyfile(db_path, db_backup)

    try:
        # seedboxsync stats by-month
        argv = ['stats', 'by-month']
        with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:

            app.run()
            data, output = app.last_rendered
            assert hashlib.md5(output.encode('utf-8')).hexdigest() == 'f97f51b36c8072c1ed887fe418a51480'

    finally:
        # Restaure database
        shutil.move(db_backup, db_path)
