# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

import os
from cement import App, fs  # type: ignore[attr-defined]
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

    def lock(self, lock_file: str) -> None:
        """
        Lock the task by creating a PID file.

        Args:
            lock_file (str): The lock file path.

        Raises:
            LockError: If the lock file cannot be created.
        """
        lock_file = fs.abspath(lock_file)
        self.app.log.debug('Lock task by %s' % lock_file)
        try:
            fs.ensure_dir_exists(os.path.dirname(lock_file))
            lock = open(lock_file, 'w+')
            lock.write(str(os.getpid()))
            lock.close()
        except Exception as exc:
            raise LockError('Lock error: %s' % str(exc))

    def unlock(self, lock_file: str) -> None:
        """
        Unlock the task by removing the PID file.

        Args:
            lock_file (str): The lock file path.

        Raises:
            LockError: If the lock file cannot be removed.
        """
        lock_file = fs.abspath(lock_file)
        self.app.log.debug('Unlock task by %s' % lock_file)
        try:
            os.remove(lock_file)
        except Exception as exc:
            raise LockError('Lock error: %s' % str(exc))

    def is_locked(self, lock_file: str) -> bool:
        """
        Check if the task is currently locked by a PID file.

        Args:
            lock_file (str): The lock file path.

        Returns:
            bool: True if the task is locked, False otherwise.
        """
        lock_file = fs.abspath(lock_file)
        if os.path.isfile(lock_file):
            pid = int(open(lock_file, 'r').readlines()[0])
            if self._check_pid(pid):
                self.app.log.info('Already running (pid=%s)' % str(pid))
                return True
            else:
                self.app.log.info('Restored from a previous crash (pid=%s)' % str(pid))

        return False

    def lock_or_exit(self, lock_file: str) -> None:
        """
        Lock the task or exit if already running.

        Args:
            lock_file (str): The lock file path.
        """
        if self.is_locked(lock_file):
            self.app.exit_code = 0
            self.app.close()
        else:
            self.lock(lock_file)

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
