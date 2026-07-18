# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
import os
from huey import crontab
from seedboxsync.core import current_app as app
from seedboxsync.core.sync.services import blackhole as blackhole_service, BLACKHOLE_LOCK_NAME as LOCK_NAME

task_manager = app.task_manager
ctx = app.app_context()
minute = os.getenv("SYNC_BLACKHOLE_MINUTE", "*")


@task_manager.periodic_task(crontab(minute=minute))  # type: ignore[untyped-decorator]
@task_manager.lock_task(LOCK_NAME)  # type: ignore[untyped-decorator]
def periodic_sync_blackhole() -> None:
    with ctx:
        blackhole_service(False, True)
