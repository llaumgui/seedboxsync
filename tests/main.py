import hashlib
from cement import TestApp
from seedboxsync.main import SeedboxSync
from contextlib import contextmanager


class SeedboxSyncTestNotUsed(TestApp, SeedboxSync):
    """A sub-class of SeedboxSync that is better suited for testing."""

    class Meta:
        label = 'seedboxsync'
        ore_system_config_files = []
        core_user_config_files = []
        config_files = []
        core_system_config_dirs = []
        core_user_config_dirs = []
        config_dirs = []
        core_system_template_dirs = []
        core_user_template_dirs = []
        core_system_plugin_dirs = []
        core_user_plugin_dirs = []
        plugin_dirs = []
        exit_on_close = False


@contextmanager
def SeedboxSyncTest(*args, **kwargs):
    with SeedboxSyncTestNotUsed(*args, **kwargs) as app:
        try:
            yield app
        finally:
            if hasattr(app, '_db'):
                app._db.close()  # close Peewee DB


def hash_output(output):
    """Return the MD5 hash of the output."""
    return hashlib.md5(output.encode('utf-8')).hexdigest()
