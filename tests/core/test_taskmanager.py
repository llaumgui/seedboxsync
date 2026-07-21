from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch
import pytest
from seedboxsync.core.taskmanager.manager import Manager
from seedboxsync.core.taskmanager.utils import load_task_modules


def test_manager_initializes_huey_next_to_application_database(app, tmp_path):
    database = tmp_path / "data" / "seedboxsync.db"
    app.config["DATABASE"] = f"sqlite:///{database}"
    huey = MagicMock()

    with patch("seedboxsync.core.taskmanager.manager.SqliteHuey", return_value=huey) as sqlite_huey:
        manager = Manager(app)

    sqlite_huey.assert_called_once_with("seedboxsync", filename=str(database.with_name("huey.db")))
    assert app.extensions["huey"] is huey
    assert manager.pending is huey.pending


def test_uninitialized_manager_rejects_proxy_access():
    manager = Manager()

    with pytest.raises(RuntimeError, match="has not been initialized"):
        _ = manager.pending


@pytest.mark.parametrize(
    ("database_url", "message"),
    [
        ("postgresql:///seedboxsync", "Unsupported database scheme"),
        ("sqlite:", "does not contain a file path"),
        ("sqlite:///:memory:", "in-memory SQLite database"),
    ],
)
def test_manager_rejects_database_urls_without_a_sqlite_file(app, database_url, message):
    app.config["DATABASE"] = database_url
    manager = Manager()
    manager.app = app

    with pytest.raises(ValueError, match=message):
        manager._get_huey_database()


def test_uninitialized_manager_cannot_derive_database_path():
    with pytest.raises(RuntimeError, match="has not been initialized"):
        Manager()._get_huey_database()


def test_load_task_modules_imports_only_task_prefixed_modules(app):
    discovered = [
        SimpleNamespace(name="task_sync_seedbox"),
        SimpleNamespace(name="helpers"),
        SimpleNamespace(name="task_sync_blackhole"),
    ]
    imported = [MagicMock(name="seedbox"), MagicMock(name="blackhole")]

    with (
        app.app_context(),
        patch("seedboxsync.core.taskmanager.utils.pkgutil.iter_modules", return_value=discovered),
        patch("seedboxsync.core.taskmanager.utils.importlib.import_module", side_effect=imported) as import_module,
    ):
        result = load_task_modules()

    assert result == imported
    assert import_module.call_args_list == [
        call("seedboxsync.core.taskmanager.task.task_sync_seedbox"),
        call("seedboxsync.core.taskmanager.task.task_sync_blackhole"),
    ]
