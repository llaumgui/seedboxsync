# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
Transport client using sFTP protocol.
"""
import os
import paramiko
import socket
from stat import S_ISDIR
from cement import App  # type: ignore[attr-defined]
from typing import Generator, Tuple, List
from paramiko.sftp_attr import SFTPAttributes
from seedboxsync.core.sync.abstract_client import AbstractClient, _Callback
from seedboxsync.core.sync.sync import ConnectionError


class SftpClient(AbstractClient):
    """
    SFTP transport client using Paramiko.

    Handles file transfers between NAS and Seedbox servers. Provides basic
    operations such as get, put, rename, chmod, and directory traversal.
    """
    __app: App
    __host: str
    __login: str
    __password: str
    __port: str
    __timeout: str | bool
    __transport = paramiko.Transport
    __client: paramiko.SFTPClient
    __max_concurrent_prefetch_requests: int

    def __init__(self, app: App):
        """
        Initialize the SFTP client with connection parameters.

        Args:
            app (App): The Cement application instance.
        """
        self.__app = app
        self.__host = self.__app.config.get('seedbox', 'host')
        self.__login = self.__app.config.get('seedbox', 'login')
        self.__password = self.__app.config.get('seedbox', 'password')
        self.__port = self.__app.config.get('seedbox', 'port')
        self.__timeout = self.__app.config.get('seedbox', 'timeout')
        self.__max_concurrent_prefetch_requests = self.__app.config.get('seedbox', 'max_concurrent_prefetch_requests')
        self.__transport = None

    def __connect_before(self) -> None:
        """
        Initialize the SFTP transport and client if not already connected.

        Raises:
            ConnectionError: If connection or authentication fails.
        """
        if self.__transport is None:
            self.__app.log.debug('Init paramiko.Transport')
            try:
                self.__transport = paramiko.Transport((self.__host, int(self.__port)))
            except (socket.gaierror, ConnectionRefusedError) as exc:
                raise ConnectionError(f"{str(exc)}\nFailed to establish a connection. " +
                                      "Ensure the host and port are correct, and that no firewall is blocking access.")

            try:
                self.__transport.connect(username=self.__login, password=self.__password)
            except paramiko.ssh_exception.AuthenticationException as exc:
                raise ConnectionError(f'{str(exc)}\nFailed to establish a connection. Ensure the login and password are correct.')

            self.__app.log.debug('Init paramiko.SFTPClient from transport')
            self.__client = paramiko.SFTPClient.from_transport(self.__transport)

            # Setup timeout
            if self.__timeout:
                channel = self.__client.get_channel()
                channel.settimeout(self.__timeout)
                self.__app.log.debug('Timeout is set to %s' % channel.gettimeout())

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

    def get(self, remote_path: str, local_path: str, progress_callback: _Callback | None = None) -> None:
        """
        Download a remote file from the SFTP server.

        Args:
            remote_path (str): Path of the remote file.
            local_path (str): Destination path on the local host.
            progress_callback (_Callback | None): Optional callback receiving bytes_transferred.
        """
        self.__connect_before()
        self.__client.get(
            remote_path,
            local_path,
            callback=progress_callback,
            max_concurrent_prefetch_requests=self.__max_concurrent_prefetch_requests
        )

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

    def chmod(self, path: str, mode: int) -> None:
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
        files: List[str] = []
        folders: List[str] = []
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
            self.__app.log.debug('Close paramiko.Transport client')
            self.__transport.close()
