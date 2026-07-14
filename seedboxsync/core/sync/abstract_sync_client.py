# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
Abstract transport client using paramiko-like interface.

This class defines the interface that all transport clients must implement,
providing methods for file operations and session management on a remote server.
"""

from abc import ABCMeta, abstractmethod
from typing import Callable
from typing_extensions import TypeAlias

_Callback: TypeAlias = Callable[[int, int], object]


class AbstractSyncClient:  # pragma: no cover
    """
    Abstract base class for transport clients.

    All concrete clients must implement methods to manage file transfers
    and remote file operations.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self) -> None:
        """
        Initialize the transport client.
        """
        pass

    @abstractmethod
    def put(self, local_path: str, remote_path: str) -> None:
        """
        Upload a local file to the remote server.

        Args:
            local_path (str): Path to the local file to copy.
            remote_path (str): Destination path on the server including filename.
                               Specifying only a directory must raise an error.
        """
        pass

    @abstractmethod
    def get(
        self,
        remotep_path: str,
        local_path: str,
        progress_callback: _Callback | None = None,
    ) -> None:
        """
        Download a file from the remote server to the local host.

        Args:
            remotep_path (str): Path to the remote file to copy.
            local_path (str): Destination path on the local host.
            progress_callback (_Callback | None): Optional callback receiving bytes_transferred.
        """
        pass

    @abstractmethod
    def stat(self, filepath: str) -> None:
        """
        Retrieve metadata about a file on the remote system.

        Returns an object similar to Python's os.stat, with fewer fields.
        Supported fields: st_mode, st_size, st_uid, st_gid, st_atime, st_mtime.

        Args:
            filepath (str): Path to the remote file.
        """
        pass

    @abstractmethod
    def chdir(self, path: str) -> None:
        """
        Change the current working directory on the remote session.

        Args:
            path (str, optional): New working directory path. Defaults to None.
        """
        pass

    @abstractmethod
    def chmod(self, path: str, mode: int) -> None:
        """
        Change permissions of a remote file.

        Permissions are unix-style, same as Python's os.chmod.

        Args:
            path (str): Path to the file on the remote server.
            mode (int): New permissions to set.
        """
        pass

    @abstractmethod
    def rename(self, old_path: str, new_path: str) -> None:
        """
        Rename a file or directory on the remote server.

        Args:
            old_path (str): Existing path of the file or folder.
            new_path (str): New path or name for the file or folder.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Close the transport session and release resources.
        """
        pass
