#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Starter for the SeedboxSync taskmanager."""

import logging
import os
from typing import Any
from seedboxsync import create_app
from seedboxsync.core import Config
from seedboxsync.core.taskmanager import heartbeat_shutdown, heartbeat_startup
from seedboxsync.core.taskmanager.utils import load_task_modules

log_level = logging.getLevelNamesMapping().get(os.getenv("HUEY_LOG_LEVEL", "INFO").upper(), logging.INFO)
app = create_app()

with app.app_context():
    huey = app.task_manager
    app.logger.setLevel(log_level)
    app.logger.info("Start huey consumer")

    @huey.on_startup()  # type: ignore[untyped-decorator]
    def on_startup() -> None:
        """Call function on huey startup."""
        heartbeat_startup()
        app.logger.debug("Flushing old tasks from queue...")
        huey.flush()

    @huey.on_shutdown()  # type: ignore[untyped-decorator]
    def on_shutdown() -> None:
        """Call function on huey shutdown."""
        heartbeat_shutdown()

    @huey.pre_execute()  # type: ignore[untyped-decorator]
    def setup_worker_logging(task: Any) -> None:
        """Configure the Huey logger from Flask."""
        huey_logger = logging.getLogger("huey")
        huey_logger.handlers = []
        for handler in app.logger.handlers:
            huey_logger.addHandler(handler)

    @huey.pre_execute()  # type: ignore[untyped-decorator]
    def reload_config(task: Any) -> None:
        """Reload Flask DB config."""
        config = Config.reload_config(app)
        app.config.from_mapping(config)

    load_task_modules()
