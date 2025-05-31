import hashlib
import os
import shutil
from seedboxsync.main import SeedboxSyncTest


config_dirs = [os.getcwd() + '/tests/resources']
db_path = config_dirs[0] + '/seedboxsync.db'
db_backup = db_path + '.bak'


def test_seedboxsync_clean():
    """
    Test clean command.
    """

    # Backup DB
    shutil.copyfile(db_path, db_backup)

    try:
        # seedboxsync clean progress
        argv = ['clean', 'progress']
        with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
            app.run()
            data, output = app.last_rendered
            assert hashlib.md5(output.encode('utf-8')).hexdigest() == 'e8a1eb752a7fb6607ec41e63aaf45ebf'

        # seedboxsync clean downloaded 607
        argv = ['clean', 'downloaded', '607']
        with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
            app.run()
            data, output = app.last_rendered
            assert hashlib.md5(output.encode('utf-8')).hexdigest() == '48d2b91a68900eef6fc440546c305830'

        # seedboxsync clean downloaded 999
        argv = ['clean', 'downloaded', '999']
        with SeedboxSyncTest(argv=argv, config_dirs=config_dirs) as app:
            app.run()
            data, output = app.last_rendered
            assert hashlib.md5(output.encode('utf-8')).hexdigest() == 'ff4b034622291f06988a584777752ae5'

    finally:
        # Restore DB
        shutil.move(db_backup, db_path)
