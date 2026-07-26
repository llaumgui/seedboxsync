#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Define a huey tasks for seedbox synchronization."""

import os
from seedboxsync.core import current_app as app
from seedboxsync.core.sync.services import (
    SEEDBOX_LOCK_NAME as LOCK_NAME,
    SEEDBOX_PRIORITY as PRIORITY,
    seedbox as seedbox_service,
)

task_manager = app.task_manager
ctx = app.app_context()
minute = os.getenv("SYNC_SEEDBOX_MINUTE", "*/15")


@task_manager.task(priority=PRIORITY)  # type: ignore[untyped-decorator]
@task_manager.lock_task(LOCK_NAME)  # type: ignore[untyped-decorator]
def sync_seedbox() -> None:
    """Define a huey task."""
    with ctx:
        seedbox_service(False, True, False)
