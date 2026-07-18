# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

import logging
from typing import Any
from seedboxsync import create_app
from seedboxsync.core import Config
from seedboxsync.core.taskmanager.utils import load_task_modules

app = create_app()

with app.app_context():
    huey = app.task_manager

    app.logger.setLevel(logging.INFO)
    app.logger.info("Start huey consumer")

    @huey.pre_execute()  # type: ignore[untyped-decorator]
    def setup_worker_logging(task: Any) -> None:
        huey_logger = logging.getLogger("huey")
        huey_logger.handlers = []
        for handler in app.logger.handlers:
            huey_logger.addHandler(handler)

    @huey.pre_execute()  # type: ignore[untyped-decorator]
    def reload_config(task: Any) -> None:
        config = Config.reload_config(app)
        app.config.from_mapping(config)

    load_task_modules()
