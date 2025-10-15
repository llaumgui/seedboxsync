# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
import os
import datetime
from cement import App  # type: ignore[attr-defined]
from seedboxsync.core.dao import Lock as LockModel
from seedboxsync.core.exc import SeedboxSyncError


class Lock(object):
    """
    Class to manage PID files (lock files) to prevent concurrent runs.
    """

    def __init__(self, app: App):
        """
        Constructor for Lock.

        Args:
            app (App): The Cement App object.
        """
        self.app = app

    def lock(self, lock_key: str) -> None:
        """
        Lock the task by upsert a lock entry.

        Args:
            lock_key (str): The lock key.
        """
        self.app.log.debug('Lock task by %s' % lock_key)
        LockModel.insert(
            key=lock_key,
            pid=os.getpid(),
            locked=True,
            locked_at=datetime.datetime.now()
        ).on_conflict(
            conflict_target=[LockModel.key],
            update={
                'pid': os.getpid(),
                'locked': True,
                'locked_at': datetime.datetime.now()
            }
        ).execute()

    def unlock(self, lock_key: str) -> None:
        """
        Unlock the task by upsert a lock entry.

        Args:
            lock_key (str): The lock key.
        """
        self.app.log.debug('Unlock task by %s' % lock_key)

        LockModel.insert(
            key=lock_key,
            pid=0,
            locked=False,
            unlocked_at=datetime.datetime.now()
        ).on_conflict(
            conflict_target=[LockModel.key],
            update={
                'pid': 0,
                'locked': False,
                'unlocked_at': datetime.datetime.now()
            }
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
        except LockModel.DoesNotExist:
            return False

        if lock.locked:
            pid = int(lock.pid)
            if self._check_pid(pid):
                self.app.log.info('Already running (pid=%s)' % str(pid))
                return True
            else:
                self.app.log.info('Restored from a previous crash (pid=%s)' % str(pid))

        return False

    def lock_or_exit(self, lock_key: str) -> None:
        """
        Lock the task or exit if already running.

        Args:
            lock_key (str): The lock key.
        """
        if self.is_locked(lock_key):
            self.app.exit_code = 0
            self.app.close()
        else:
            self.lock(lock_key)

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


def lock_pre_run_hook(app: App) -> None:
    """
    Post-setup hook to extend SeedboxSync with Lock support.

    Args:
        app (App): The Cement App object.
    """
    app.log.debug('Extending seedboxsync application with Lock')
    app.extend('lock', Lock(app))


def load(app: App) -> None:
    """
    Registers the Lock pre-run hook.

    Args:
        app (App): The Cement App object.
    """
    app.hook.register('pre_run', lock_pre_run_hook)
