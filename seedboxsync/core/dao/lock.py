# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from peewee import BooleanField, CharField, DateTimeField, IntegerField
from seedboxsync.core.dao import SeedboxSyncModel


class Lock(SeedboxSyncModel):
    """
    Represents a lock record in the system to prevent concurrent processes.

    Attributes:
        key (str): Unique identifier for the lock, e.g., 'sync_blackhole'.
        pid (int): The process ID that holds the lock.
        locked (bool): Indicates whether the lock is currently active.
        locked_at (datetime): Timestamp when the lock was acquired.
        unlocked_at (datetime): Timestamp when the lock was released.
    """

    key = CharField(primary_key=True, help_text="Unique lock identifier")
    pid = IntegerField(help_text="Process ID holding the lock")
    locked = BooleanField(default=False, help_text="Whether the lock is currently active")
    locked_at = DateTimeField(null=True, help_text="Timestamp when the lock was acquired")
    unlocked_at = DateTimeField(null=True, help_text="Timestamp when the lock was released")
