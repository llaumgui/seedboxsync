from tests.main import SeedboxSyncTest
from seedboxsync.ext.ext_lock import Lock


def test_lock(tmp):
    """
    Test lock / unlock is locked.
    """

    _, tmp_config_files, _, _ = tmp

    with SeedboxSyncTest(config_files=tmp_config_files) as app:
        lock = Lock(app)

        lock.lock('test')
        assert lock.is_locked('test') is True

        lock.unlock('test')
        assert lock.is_locked('test') is False

        app.run()  # Run to close safty
