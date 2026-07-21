#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Track task status by decorator."""

from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import ParamSpec, TypeVar
from seedboxsync.core.dao import TaskStatus

P = ParamSpec("P")
R = TypeVar("R")


def track_taskstatus(key: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Track the execution status of a task in the database.

    Args:
        key: Unique identifier used to store the task status.

    Returns:
        A decorator that updates the task status before and after execution.
    """

    def decorator(function: Callable[P, R]) -> Callable[P, R]:
        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            started = datetime.now()

            TaskStatus.insert(
                key=key,
                running=True,
                started=started,
                finished=None,
            ).on_conflict(
                conflict_target=[TaskStatus.key],
                update={
                    TaskStatus.running: True,
                    TaskStatus.started: started,
                    TaskStatus.finished: None,
                },
            ).execute()

            try:
                return function(*args, **kwargs)
            finally:
                TaskStatus.update(
                    running=False,
                    finished=datetime.now(),
                ).where(
                    TaskStatus.key == key,
                ).execute()

        return wrapper

    return decorator
