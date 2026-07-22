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
from collections.abc import Callable
from os import PathLike

_Callback = Callable[[int, int], object]

PathType = str | PathLike[str]


class AbstractSyncClient:  # pragma: no cover
    """
    Abstract base class for transport clients.

    All concrete clients must implement methods to manage file transfers
    and remote file operations.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self) -> None:
        """Initialize the transport client."""

    @abstractmethod
    def put(self, local_path: PathType, remote_path: PathType) -> None:
        """
        Upload a local file to the remote server.

        Args:
            local_path (PathType): Path to the local file to copy.
            remote_path (PathType): Destination path on the server including filename.
                               Specifying only a directory must raise an error.
        """

    @abstractmethod
    def get(
        self,
        remote_path: PathType,
        local_path: PathType,
        progress_callback: _Callback | None = None,
    ) -> None:
        """
        Download a file from the remote server to the local host.

        Args:
            remote_path (PathType): Path to the remote file to copy.
            local_path (PathType): Destination path on the local host.
            progress_callback (_Callback | None): Optional callback receiving bytes_transferred.
        """

    @abstractmethod
    def stat(self, filepath: PathType) -> None:
        """
        Retrieve metadata about a file on the remote system.

        Returns an object similar to Python's os.stat, with fewer fields.
        Supported fields: st_mode, st_size, st_uid, st_gid, st_atime, st_mtime.

        Args:
            filepath (PathType): Path to the remote file.
        """

    @abstractmethod
    def chdir(self, path: PathType) -> None:
        """
        Change the current working directory on the remote session.

        Args:
            path (PathType, optional): New working directory path. Defaults to None.
        """

    @abstractmethod
    def chmod(self, path: PathType, mode: int) -> None:
        """
        Change permissions of a remote file.

        Permissions are unix-style, same as Python's os.chmod.

        Args:
            path (PathType): Path to the file on the remote server.
            mode (int): New permissions to set.
        """

    @abstractmethod
    def rename(self, old_path: PathType, new_path: PathType) -> None:
        """
        Rename a file or directory on the remote server.

        Args:
            old_path (stPathTyper): Existing path of the file or folder.
            new_path (PathType): New path or name for the file or folder.
        """

    @abstractmethod
    def close(self) -> None:
        """Close the transport session and release resources."""
