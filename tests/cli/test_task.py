import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest
from seedboxsync.cli import cli


@pytest.fixture
def task_manager(app):
    manager = MagicMock()
    app.__dict__["task_manager"] = manager
    return manager


def test_task_result_renders_result_keys(runner, task_manager):
    task_manager.all_results.return_value = ["result-1", "result-2"]

    result = runner.invoke(cli, ["task", "result"])

    assert result.exit_code == 0
    assert "Result key" in result.output
    assert "result-1" in result.output
    assert "result-2" in result.output


def test_task_pending_supports_huey_objects_and_string_fallback(runner, task_manager):
    task_manager.pending.return_value = [
        SimpleNamespace(name="sync_seedbox", id="task-1"),
        "sync_blackhole: task-2",
    ]

    result = runner.invoke(cli, ["task", "pending"])

    assert result.exit_code == 0
    assert "sync_seedbox" in result.output
    assert "task-1" in result.output
    assert "sync_blackhole" in result.output
    assert "task-2" in result.output


def test_task_list_loads_modules_before_rendering_registry(runner, task_manager):
    task_manager._registry._registry = ["sync_blackhole", "sync_seedbox"]

    with patch("seedboxsync.cli.commands.cmd_task.load_task_modules") as load_modules:
        result = runner.invoke(cli, ["task", "list"])

    assert result.exit_code == 0
    load_modules.assert_called_once_with()
    assert "sync_blackhole" in result.output
    assert "sync_seedbox" in result.output


@pytest.mark.parametrize(
    ("command", "method", "message"),
    [
        ("flush", "flush", "Queue flushed"),
        ("flush-lock", "flush_locks", "Lock flushed"),
    ],
)
def test_task_flush_commands_delegate_to_manager(runner, task_manager, command, method, message):
    result = runner.invoke(cli, ["task", command])

    assert result.exit_code == 0
    getattr(task_manager, method).assert_called_once_with()
    assert message in result.output


@pytest.mark.parametrize(
    ("command", "module_name", "function_name", "message"),
    [
        (
            "sync-blackhole",
            "seedboxsync.core.taskmanager.task.task_sync_blackhole",
            "sync_blackhole",
            "Task sync blackhole launched",
        ),
        (
            "sync-seedbox",
            "seedboxsync.core.taskmanager.task.task_sync_seedbox",
            "sync_seedbox",
            "Task sync seedbox launched",
        ),
    ],
)
def test_task_sync_commands_enqueue_expected_task(runner, task_manager, command, module_name, function_name, message):
    module = ModuleType(module_name)
    task = MagicMock()
    setattr(module, function_name, task)

    with patch.dict(sys.modules, {module_name: module}):
        result = runner.invoke(cli, ["task", command])

    assert result.exit_code == 0
    task.assert_called_once_with()
    assert message in result.output
