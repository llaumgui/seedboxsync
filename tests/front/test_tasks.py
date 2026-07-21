from datetime import datetime
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch
import pytest
from seedboxsync.__version__ import __api_path_version__ as api_path_version
from seedboxsync.core.dao import TaskStatus

API_PATH = f"/api/{api_path_version}"


@pytest.mark.parametrize(
    ("key", "module_name", "function_name"),
    [
        ("seedbox", "seedboxsync.core.taskmanager.task.task_sync_seedbox", "sync_seedbox"),
        ("blackhole", "seedboxsync.core.taskmanager.task.task_sync_blackhole", "sync_blackhole"),
    ],
)
def test_task_api_enqueues_known_tasks(client, key, module_name, function_name):
    module = ModuleType(module_name)
    task = MagicMock()
    setattr(module, function_name, task)

    with patch.dict(sys.modules, {module_name: module}):
        response = client.post(f"{API_PATH}/tasks/{key}")

    assert response.status_code == 202
    assert response.json == {"status": "queued", "task": key}
    task.assert_called_once_with()


def test_task_api_rejects_unknown_tasks(client):
    response = client.post(f"{API_PATH}/tasks/unknown")

    assert response.status_code == 404
    assert "unknown" in response.json["message"]


def test_taskstatus_api_lists_and_returns_statuses(app, client):
    now = datetime.now().replace(microsecond=0)
    with app.app_context():
        TaskStatus.replace(key="sync_seedbox", running=False, started=now, finished=now).execute()
        app.extensions["flaskdb"].database.close()

    list_response = client.get(f"{API_PATH}/taskstatuses")
    detail_response = client.get(f"{API_PATH}/taskstatuses/sync_seedbox")

    assert list_response.status_code == 200
    assert list_response.json["type"] == "TaskStatus"
    assert any(item["key"] == "sync_seedbox" for item in list_response.json["data"])
    assert detail_response.status_code == 200
    assert detail_response.json["data"]["key"] == "sync_seedbox"


def test_taskstatus_api_returns_404_for_unknown_status(client):
    response = client.get(f"{API_PATH}/taskstatuses/unknown")

    assert response.status_code == 404
    assert "unknown" in response.json["message"]
