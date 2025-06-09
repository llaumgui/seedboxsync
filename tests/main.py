import os
import shutil
import hashlib
from cement import TestApp
from seedboxsync.main import SeedboxSync

config_dirs = [os.getcwd() + '/tests/resources']
db_path = config_dirs[0] + '/seedboxsync.db'
watch_path = config_dirs[0] + '/watch'
watch_torrent_path = watch_path + '/Fedora-Server-dvd-x86_64-32.torrent'
db_backup = db_path + '.bak'
watch_backup = watch_path + '.bak'


class SeedboxSyncTest(TestApp, SeedboxSync):
    """A sub-class of SeedboxSync that is better suited for testing."""

    class Meta:
        label = 'seedboxsync'

    def get_config_dirs():
        """Return the test config directories."""
        return config_dirs

    def get_watch_torrent_path():
        """Return testing torrent path."""
        return watch_torrent_path

    def backup_db():
        """Backup the database."""
        shutil.copyfile(db_path, db_backup)

    def restore_db():
        """Restore the database from the backup."""
        shutil.move(db_backup, db_path)

    def backup_and_clean_watch():
        """Backup the watch folder and clean it."""
        SeedboxSyncTest.backup_watch()
        os.remove(watch_path + '/Fedora-Server-dvd-x86_64-32.torrent')

    def backup_watch():
        """Backup the watch folder."""
        shutil.rmtree(watch_backup, ignore_errors=True)
        shutil.copytree(watch_path, watch_backup)
        SeedboxSyncTest.backup_db()

    def restore_watch():
        """Restore the watch folder from the backup."""
        shutil.rmtree(watch_path)
        shutil.move(watch_backup, watch_path)
        SeedboxSyncTest.restore_db()

    def hash_output(output):
        """Return the MD5 hash of the output."""
        return hashlib.md5(output.encode('utf-8')).hexdigest()
