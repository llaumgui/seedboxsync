import importlib
import sys
from unittest.mock import MagicMock, patch
import pytest


def _identity_decorator(*args, **kwargs):
    def decorate(function):
        return function

    return decorate


@pytest.mark.parametrize(
    ("module_name", "periodic_name", "task_name", "service_name", "service_args", "environment_name", "environment_value"),
    [
        (
            "seedboxsync.core.taskmanager.task.task_sync_blackhole",
            "periodic_sync_blackhole",
            "sync_blackhole",
            "blackhole_service",
            (False, True),
            "SYNC_BLACKHOLE_MINUTE",
            "10",
        ),
        (
            "seedboxsync.core.taskmanager.task.task_sync_seedbox",
            "periodic_sync_seedbox",
            "sync_seedbox",
            "seedbox_service",
            (False, True, False),
            "SYNC_SEEDBOX_MINUTE",
            "20",
        ),
    ],
)
def test_task_modules_register_and_execute_periodic_and_manual_tasks(
    app,
    monkeypatch,
    module_name,
    periodic_name,
    task_name,
    service_name,
    service_args,
    environment_name,
    environment_value,
):
    manager = MagicMock()
    manager.periodic_task.side_effect = _identity_decorator
    manager.lock_task.side_effect = _identity_decorator
    manager.task.side_effect = _identity_decorator
    app.__dict__["task_manager"] = manager
    monkeypatch.setenv(environment_name, environment_value)

    with patch.dict(sys.modules), app.app_context():
        sys.modules.pop(module_name, None)
        module = importlib.import_module(module_name)
        service = MagicMock()
        setattr(module, service_name, service)

        getattr(module, periodic_name)()
        getattr(module, task_name)()

    assert module.minute == environment_value
    manager.periodic_task.assert_called_once()
    manager.lock_task.assert_called()
    manager.task.assert_called_once_with()
    assert service.call_args_list[0].args == service_args
    assert service.call_args_list[1].args == service_args
