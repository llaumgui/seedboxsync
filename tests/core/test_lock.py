from unittest.mock import patch

from seedboxsync.core.dao import Lock as LockModel
from seedboxsync.core.lock import Lock


def test_lock_and_unlock_are_persisted(app):
    with app.app_context():
        lock = Lock()
        with patch.object(lock, "_check_pid", return_value=True):
            lock.lock("test")
            assert lock.is_locked("test") is True

        row = LockModel.get_by_id("test")
        assert row.locked is True
        assert row.pid > 0
        assert row.locked_at is not None

        lock.unlock("test")
        row = LockModel.get_by_id("test")
        assert row.locked is False
        assert row.pid == 0
        assert row.unlocked_at is not None
        assert lock.is_locked("test") is False


def test_unknown_lock_is_not_locked(app):
    with app.app_context():
        assert Lock().is_locked("missing") is False


def test_stale_lock_can_be_reacquired(app):
    with app.app_context():
        lock = Lock()
        lock.lock("stale")
        with patch.object(lock, "_check_pid", return_value=False):
            assert lock.is_locked("stale") is False
            assert lock.lock_or_exit("stale") is True


def test_active_lock_cannot_be_reacquired(app):
    with app.app_context():
        lock = Lock()
        lock.lock("active")
        with patch.object(lock, "_check_pid", return_value=True):
            assert lock.lock_or_exit("active") is False
