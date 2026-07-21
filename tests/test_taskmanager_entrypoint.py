import importlib
import logging
import sys
from unittest.mock import MagicMock, patch


def _capture_decorator(callbacks, name):
    def factory():
        def decorate(function):
            callbacks.setdefault(name, []).append(function)
            return function

        return decorate

    return factory


def test_taskmanager_entrypoint_registers_worker_hooks(app, monkeypatch):
    callbacks = {}
    huey = MagicMock()
    huey.on_startup.side_effect = _capture_decorator(callbacks, "startup")
    huey.pre_execute.side_effect = _capture_decorator(callbacks, "pre_execute")
    app.__dict__["task_manager"] = huey
    monkeypatch.setenv("HUEY_LOG_LEVEL", "debug")

    with (
        patch.dict(sys.modules),
        patch("seedboxsync.create_app", return_value=app) as create_app,
        patch("seedboxsync.core.taskmanager.utils.load_task_modules") as load_modules,
        patch("seedboxsync.core.Config.reload_config", return_value={"RELOADED": True}) as reload_config,
    ):
        sys.modules.pop("seedboxsync.taskmanager", None)
        module = importlib.import_module("seedboxsync.taskmanager")

        module.flush()
        worker_logger = MagicMock()
        app.logger.handlers = [MagicMock(), MagicMock()]
        with patch("seedboxsync.taskmanager.logging.getLogger", return_value=worker_logger):
            module.setup_worker_logging(None)
        module.reload_config(None)

    create_app.assert_called_once_with()
    load_modules.assert_called_once_with()
    assert module.log_level == logging.DEBUG
    assert len(callbacks["startup"]) == 1
    assert len(callbacks["pre_execute"]) == 2
    huey.flush.assert_called_once_with()
    worker_logger.addHandler.assert_any_call(app.logger.handlers[0])
    worker_logger.addHandler.assert_any_call(app.logger.handlers[1])
    reload_config.assert_called_once_with(app)
    assert app.config["RELOADED"] is True
