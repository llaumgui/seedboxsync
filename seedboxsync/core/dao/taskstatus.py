#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Peewee DAO model for TaskStatus."""

from peewee import BooleanField, CharField, DateTimeField
from seedboxsync.core.dao import SeedboxSyncModel


class TaskStatus(SeedboxSyncModel):
    """
    Represents a taskstatus record in the system to prevent concurrent processes.

    Attributes:
        key (str): Unique identifier for the task, e.g., 'sync_blackhole'.
        running (bool): Indicates whether the task is currently running.
        started (datetime): Timestamp when the task execution started.
        finished (datetime): Timestamp when the task execution finished.
    """

    key = CharField(primary_key=True, help_text="Unique task identifier")
    running = BooleanField(default=False, help_text="Whether the task is currently running")
    started = DateTimeField(null=True, help_text="Timestamp when the task execution started")
    finished = DateTimeField(null=True, help_text="Timestamp when the task execution finished")
