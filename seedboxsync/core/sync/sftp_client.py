# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
Transport client using sFTP protocol.
"""
import os
import paramiko  # type: ignore[import-untyped]
from stat import S_ISDIR
from cement.core.log import LogInterface
from typing import Generator, Tuple, List
from paramiko.sftp_attr import SFTPAttributes  # type: ignore[import-untyped]
from seedboxsync.core.sync.abstract_client import AbstractClient
from seedboxsync.core.sync.sync import ConnectionError


class SftpClient(AbstractClient):
    """
    SFTP transport client using Paramiko.

    Handles file transfers between NAS and Seedbox servers. Provides basic
    operations such as get, put, rename, chmod, and directory traversal.
    """
    __log: LogInterface
    __host: str
    __login: str
    __password: str
    __port: str
    __timeout: str | bool
    __transport = paramiko.Transport
    __client: paramiko.SFTPClient

    def __init__(self, log: LogInterface, host: str, login: str, password: str, port: str = "22", timeout: str | bool = False):
        """
        Initialize the SFTP client with connection parameters.

        Args:
            log (LogInterface): Logger instance.
            host (str): SFTP server hostname.
            login (str): Username for authentication.
            password (str): Password for authentication.
            port (str): Server port (default: '22').
            timeout (str | bool): Socket timeout in seconds (default: False, no timeout).
        """
        self.__log = log
        self.__host = host
        self.__login = login
        self.__password = password
        self.__port = port
        self.__timeout = timeout
        self.__transport = None

    def __connect_before(self) -> None:
        """
        Initialize the SFTP transport and client if not already connected.

        Raises:
            ConnectionError: If authentication fails.
        """
        if self.__transport is None:
            self.__log.debug('Init paramiko.Transport')
            self.__transport = paramiko.Transport((self.__host, int(self.__port)))
            try:
                self.__transport.connect(username=self.__login, password=self.__password)
            except paramiko.ssh_exception.AuthenticationException as exc:
                raise ConnectionError('Connection fail: %s' % str(exc))

            self.__client = paramiko.SFTPClient.from_transport(self.__transport)

            # Setup timeout
            if self.__timeout:
                channel = self.__client.get_channel()
                channel.settimeout(self.__timeout)
                self.__log.debug('Timeout is set to %s' % channel.gettimeout())

    def put(self, local_path: str, remote_path: str) -> SFTPAttributes:
        """
        Upload a local file to the SFTP server.

        Args:
            local_path (str): Path to the local file.
            remote_path (str): Destination path on the server (including filename).

        Returns:
            SFTPAttributes: Metadata of the uploaded file.
        """
        self.__connect_before()
        return self.__client.put(local_path, remote_path)

    def get(self, remote_path: str, local_path: str) -> None:
        """
        Download a remote file from the SFTP server.

        Args:
            remote_path (str): Path of the remote file.
            local_path (str): Destination path on the local host.
        """
        self.__connect_before()
        self.__client.get(remote_path, local_path)

    def stat(self, filepath: str) -> SFTPAttributes:
        """
        Retrieve metadata for a remote file.

        Args:
            filepath (str): Remote file path.

        Returns:
            SFTPAttributes: Object with attributes similar to Python's os.stat:
                st_mode, st_size, st_uid, st_gid, st_atime, st_mtime.
        """
        self.__connect_before()
        return self.__client.stat(filepath)

    def chdir(self, path: str | None = None) -> None:
        """
        Change the current working directory of the SFTP session.

        Args:
            path (Optional[str]): Target directory. If None, no change occurs.
        """
        self.__connect_before()
        self.__client.chdir(path)

    def chmod(self, path: str, mode: str) -> None:
        """
        Change the mode (permissions) of a remote file.

        Args:
            path (str): Path of the file.
            mode (int): Unix-style permissions (like os.chmod).
        """
        self.__connect_before()
        self.__client.chmod(path, mode)

    def rename(self, old_path: str, new_path: str) -> None:
        """
        Rename a file or directory on the remote server.

        Args:
            old_path (str): Existing path.
            new_path (str): New path.
        """
        self.__client.posix_rename(old_path, new_path)

    def walk(self, remote_path: str) -> Generator[Tuple[str, List[str], List[str]], None, None]:
        """
        Walk through remote directories, yielding paths, folders, and files.

        Args:
            remote_path (str): Remote directory to traverse.

        Yields:
            Tuple[str, List[str], List[str]]: (current_path, folders, files)

        Note:
            Simplified version of os.walk for SFTP. Efficient for large directories.

        Source:
            https://gist.github.com/johnfink8/2190472
        """
        self.__connect_before()
        path = remote_path
        files = []
        folders = []
        for f in self.__client.listdir_attr(remote_path):
            if S_ISDIR(f.st_mode):
                folders.append(f.filename)
            else:
                files.append(f.filename)
        yield path, folders, files

        for folder in folders:
            new_path = os.path.join(remote_path, folder)
            for x in self.walk(new_path):
                yield x

    def close(self) -> None:
        """
        Close the SFTP transport client and underlying connection.
        """
        if self.__transport is not None:
            self.__log.debug('Close paramiko.Transport client')
            self.__transport.close()
