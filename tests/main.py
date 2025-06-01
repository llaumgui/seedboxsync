import os
import shutil
import hashlib
from cement import TestApp
from seedboxsync.main import SeedboxSync


config_dirs = [os.getcwd() + '/tests/resources']
db_path = config_dirs[0] + '/seedboxsync.db'
db_backup = db_path + '.bak'


class SeedboxSyncTest(TestApp, SeedboxSync):
    """A sub-class of SeedboxSync that is better suited for testing."""

    class Meta:
        label = 'seedboxsync'

    def get_config_dirs():
        """Return the test config directories."""
        return config_dirs

    def get_db_path():
        """Return the test database path."""
        return db_path

    def get_db_backup():
        """Return the test database backup path."""
        return db_backup

    def backup_db():
        """Backup the database."""
        shutil.copyfile(db_path, db_backup)

    def restore_db():
        """Restore the database from the backup."""
        shutil.move(db_backup, db_path)

    def hash_output(output):
        """Return the MD5 hash of the output."""
        return hashlib.md5(output.encode('utf-8')).hexdigest()
