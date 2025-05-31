# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

import os
from cement import App, fs
from ..core.exc import SeedboxSyncError


class Lock(object):
    """
    Class which manage PID file a.k.a lock file.
    """

    def __init__(self, app: App):
        """
        Constructor

        :param App app: the Cement App object
        """
        self.app = app

    def lock(self, lock_file: str):
        """
        Lock task by a pid file to prevent launch two time.

        :param str lock_file: the lock file path
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

    def unlock(self, lock_file: str):
        """
        Unlock task, remove pid file.

        :param str lock_file: the lock file path
        """
        lock_file = fs.abspath(lock_file)
        self.app.log.debug('Unlock task by %s' % lock_file)
        try:
            os.remove(lock_file)
        except Exception as exc:
            raise LockError('Lock error: %s' % str(exc))

    def is_locked(self, lock_file: str):
        """
        Test if task is locked by a pid file to prevent launch two time.

        :param str lock_file: the lock file path
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

    def lock_or_exit(self, lock_file: str):
        """
        Lock task or exit if already running.

        :param str lock_file: the lock file path
        """
        if self.is_locked(lock_file):
            self.app.exit_code = 0
            self.app.close()
        else:
            self.lock(lock_file)

    def _check_pid(self, pid: int):
        """
        Check for the existence of a unix pid.

        :param int pid: the pid of the process
        """
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True


class LockError(SeedboxSyncError):
    pass


def lock_pre_run_hook(app: App):
    """
    Extends SeedboxSync with Lock

    :param App app: the Cement App object
    """
    app.log.debug('Extending seedboxsync application with Lock')
    app.extend('lock', Lock(app))


def load(app: App):
    """Extension loader"""
    app.hook.register('pre_run', lock_pre_run_hook)
