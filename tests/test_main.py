import os
import shutil
from tests.main import SeedboxSyncTest
from seedboxsync.core.dao import SeedboxSync
from seedboxsync.core.db import Database
from seedboxsync import __version__


def test_seedboxsync(tmp):
    """
    Test seedboxsync without any subcommands or arguments.
    """

    _, tmp_config_files, _, _ = tmp
    with SeedboxSyncTest(config_files=tmp_config_files) as app:
        app.run()
        assert app.exit_code == 0


def test_seedboxsync_create_db(tmp):
    """
    Test seedboxsync without any subcommands or arguments.
    """

    _, tmp_config_files, tmp_db, _ = tmp
    os.remove(tmp_db)

    with SeedboxSyncTest(config_files=tmp_config_files) as app:
        app.run()
        assert app.exit_code == 0
        assert Database.DATABASE_VERSION == int(SeedboxSync.get_db_version())
        assert __version__ == SeedboxSync.get_version()


def test_seedboxsync_migrate_db(tmp):
    """
    Test seedboxsync without any subcommands or arguments.
    """

    _, tmp_config_files, tmp_db, _ = tmp
    os.remove(tmp_db)
    test_db = os.path.abspath("tests/resources/seedboxsync_v1.db")
    shutil.copy(test_db, tmp_db)

    with SeedboxSyncTest(config_files=tmp_config_files) as app:
        app.run()
        assert app.exit_code == 0
        assert Database.DATABASE_VERSION == int(SeedboxSync.get_db_version())
        assert __version__ == SeedboxSync.get_version()


def test_seedboxsync_debug(tmp):
    """
    Test that debug mode is functional.
    """

    _, tmp_config_files, _, _ = tmp

    with SeedboxSyncTest(config_files=tmp_config_files) as app:
        app.run()
        assert app.debug is False
        assert app.quiet is False

    argv = ['--debug']
    with SeedboxSyncTest(config_files=tmp_config_files, argv=argv) as app:
        app.run()
        assert app.debug is True

    argv = ['-d']
    with SeedboxSyncTest(config_files=tmp_config_files, argv=argv) as app:
        app.run()
        assert app.debug is True

    argv = ['--quiet']
    with SeedboxSyncTest(config_files=tmp_config_files, argv=argv) as app:
        app.run()
        assert app.quiet is True

    argv = ['-q']
    with SeedboxSyncTest(config_files=tmp_config_files, argv=argv) as app:
        app.run()
        assert app.quiet is True
