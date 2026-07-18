# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from huey import crontab
from seedboxsync.core import current_app as app
from seedboxsync.core.taskmanager import track_taskstatus

task_manager = app.task_manager
ctx = app.app_context()
LOCK_NAME = "heartbeat"


@task_manager.periodic_task(crontab(minute="*"))  # type: ignore[untyped-decorator]
@task_manager.lock_task(LOCK_NAME)  # type: ignore[untyped-decorator]
@track_taskstatus(LOCK_NAME)
def periodic_heartbeat() -> None:
    with ctx:
        app.logger.debug("Run heartbeat")
