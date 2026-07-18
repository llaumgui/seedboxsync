# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from huey import crontab
from seedboxsync.core import current_app as app
from seedboxsync.core.sync.services import seedbox as seedbox_service, SEEDBOX_LOCK_NAME as LOCK_NAME

task_manager = app.task_manager
ctx = app.app_context()


@task_manager.periodic_task(crontab(minute="*/15"))  # type: ignore[untyped-decorator]
@task_manager.lock_task(LOCK_NAME)  # type: ignore[untyped-decorator]
def periodic_sync_seedbox() -> None:
    with ctx:
        app.logger.info("This task runs every minute")
        seedbox_service(False, True, False)
