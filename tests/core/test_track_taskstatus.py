from seedboxsync.core.dao import TaskStatus
from seedboxsync.core.taskmanager import heartbeat_shutdown, heartbeat_startup


def test_heartbeat_startup_and_shutdown_update_status(app):
    with app.app_context():
        heartbeat_startup()
        status = TaskStatus.get_by_id("heartbeat")
        assert status.running is True
        assert status.started is not None

        heartbeat_shutdown()
        status = TaskStatus.get_by_id("heartbeat")
        assert status.running is False
        assert status.finished is not None
