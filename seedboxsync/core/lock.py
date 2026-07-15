# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
"""
Lock management for SeedboxSync.
"""

import os
import datetime
from seedboxsync.core import current_app
from seedboxsync.core.dao import Lock as LockModel
from seedboxsync.cli.exception import SeedboxSyncError


class Lock(object):
    """
    Class to manage PID files (lock files) to prevent concurrent runs.
    """

    def __init__(self) -> None:
        """
        Constructor for Lock.
        """
        self.app = current_app

    def lock(self, lock_key: str) -> None:
        """
        Lock the task by upsert a lock entry.

        Args:
            lock_key (str): The lock key.
        """
        self.app.logger.debug("Lock task by %s" % lock_key)
        LockModel.insert(
            key=lock_key,
            pid=os.getpid(),
            locked=True,
            locked_at=datetime.datetime.now(),
        ).on_conflict(
            conflict_target=[LockModel.key],
            update={
                "pid": os.getpid(),
                "locked": True,
                "locked_at": datetime.datetime.now(),
            },
        ).execute()

    def unlock(self, lock_key: str) -> None:
        """
        Unlock the task by upsert a lock entry.

        Args:
            lock_key (str): The lock key.
        """
        self.app.logger.debug("Unlock task by %s" % lock_key)

        LockModel.insert(key=lock_key, pid=0, locked=False, unlocked_at=datetime.datetime.now()).on_conflict(
            conflict_target=[LockModel.key],
            update={"pid": 0, "locked": False, "unlocked_at": datetime.datetime.now()},
        ).execute()

    def is_locked(self, lock_key: str) -> bool:
        """
        Check if the task is currently locked by a PID file.

        Args:
            lock_key (str): The lock key.

        Returns:
            bool: True if the task is locked, False otherwise.
        """
        try:
            lock = LockModel.get(LockModel.key == lock_key)
        except LockModel.DoesNotExist:  # type: ignore[attr-defined]
            return False

        if lock.locked:
            pid = int(lock.pid)
            if self._check_pid(pid):
                self.app.logger.info("Already running (pid=%s)" % str(pid))
                return True
            else:
                self.app.logger.info("Restored from a previous crash (pid=%s)" % str(pid))

        return False

    def lock_or_exit(self, lock_key: str) -> bool:
        """
        Lock the task or exit if already running.

        Args:
            lock_key (str): The lock key.
        """
        if self.is_locked(lock_key):
            return False

        self.lock(lock_key)
        return True

    def _check_pid(self, pid: int) -> bool:
        """
        Check if a Unix process with the given PID exists.

        Args:
            pid (int): The PID to check.

        Returns:
            bool: True if the process exists, False otherwise.
        """
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True


class LockError(SeedboxSyncError):
    """
    Exception raised for lock-related errors.
    """

    pass
